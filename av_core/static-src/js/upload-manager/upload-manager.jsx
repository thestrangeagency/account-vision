import React from 'react';
import PropTypes from 'prop-types';
import Dropzone from 'react-dropzone';

import UploadApiService from '../services/upload-api-service';
import S3UploadService from '../services/s3-upload-service';
import File from '../shared/file/file';
import ProgressBar from '../shared/progress-bar/progress-bar';
import DeleteConfirmationModal from '../shared/delete-confirmation-modal/delete-confirmation-modal';
import UploadModal from './upload-modal/upload-modal';
import { bytesToSize, getFormattedDate } from '../utils';

const DELETE_ERROR = 'Whoops, something went wrong deleting your file. Please try again.';
const EDIT_ERROR = 'Whoops, something went wrong editing your file. Please try again.';
const FETCH_ERROR = 'Whoops, something went wrong fetching your files. Please try again.';
const UPLOAD_ERROR = 'Whoops, something went wrong uploading your file. Please try again.';

export default class UploadManager extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      error: null,
      files: [],
      focusedFileIndex: null, // the file that a delete modal targets
      isConfirmDeleteDisabled: false,
      isModalSaveDisabled: false,
      uploadsInProgress: {},
    };

    this.onClickDelete = this.onClickDelete.bind(this);
    this.onClickDeleteConfirm = this.onClickDeleteConfirm.bind(this);
    this.onDroppedFiles = this.onDroppedFiles.bind(this);
    this.onUploadModalHidden = this.onUploadModalHidden.bind(this);
    this.onUploadModalShown = this.onUploadModalShown.bind(this);
    this.onUploadProgress = this.onUploadProgress.bind(this);
    this.onSubmitModal = this.onSubmitModal.bind(this);
  }

  componentDidMount() {
    this.fetchFiles();
  }

  onDroppedFiles(files) {
    this.setState({ error: null });

    const uploadPromises = [];
    for (let i = 0; i < files.length; i += 1) {
      uploadPromises.push(this.uploadFile(files[i]));
    }

    Promise.all(uploadPromises)
      .then(() => {
        this.setState({ uploadsInProgress: {} });
        this.fetchFiles();
      })
      .catch(() => {
        this.setState({ error: UPLOAD_ERROR, uploadsInProgress: {} });
      });
  }

  onClickDelete(fileIndex) {
    this.setState({ error: null, focusedFileIndex: fileIndex }, () => {
      this.confirmDeleteModalEl.show();
    });
  }

  onClickEdit(fileIndex) {
    this.setState({ error: null, focusedFileIndex: fileIndex }, () => {
      const { files } = this.state;
      const file = files[fileIndex];

      this.inputUploadDescriptionEl.value = file.description;

      this.uploadModalEl.show();
    });
  }

  onClickDeleteConfirm() {
    const { focusedFileIndex } = this.state;

    this.deleteFile(focusedFileIndex);
  }

  onSubmitModal() {
    const description = this.inputUploadDescriptionEl.value;

    const { files, focusedFileIndex } = this.state;
    const file = files[focusedFileIndex];

    this.setState({ isModalSaveDisabled: true });

    UploadApiService.updateFile(file.url, description)
      .then((updatedFile) => {
        this.setState({
          files: [
            ...files.slice(0, focusedFileIndex),
            updatedFile,
            ...files.slice(focusedFileIndex + 1),
          ],
          isModalSaveDisabled: false,
        });
        this.uploadModalEl.hide();
      })
      .catch((ex) => {
        const { generalError } = ex;

        this.setState({
          error: generalError || EDIT_ERROR,
          isModalSaveDisabled: false,
        });
        this.uploadModalEl.hide();
      });
  }

  onUploadModalHidden() {
    this.setState({
      focusedFileIndex: null,
    });
  }

  onUploadModalShown() {
    this.inputUploadDescriptionEl.focus();
  }

  onUploadProgress(file, progress) {
    this.setFileProgress(file.name, progress);
  }

  setFileProgress(name, progress, callback) {
    this.setState(
      prevState => ({
        uploadsInProgress: {
          ...prevState.uploadsInProgress,
          [name]: { progress },
        },
      }),
      callback,
    );
  }

  deleteFile(fileIndex) {
    const { files } = this.state;
    const file = files[fileIndex];

    this.setState({ isConfirmDeleteDisabled: true });

    UploadApiService.deleteFile(file.url)
      .then(() => {
        this.setState({
          files: [...files.slice(0, fileIndex), ...files.slice(fileIndex + 1)],
          focusedFileIndex: null,
          isConfirmDeleteDisabled: false,
        });

        this.confirmDeleteModalEl.hide();
      })
      .catch(() => {
        this.setState({ error: DELETE_ERROR, isConfirmDeleteDisabled: false });
        this.confirmDeleteModalEl.hide();
      });
  }

  fetchFiles() {
    const { year, target } = this.props;

    UploadApiService.getFiles(year, target)
      .then(files => this.setState({ files }))
      .catch(() => {
        this.setState({ error: FETCH_ERROR });
      });
  }

  uploadFile(file) {
    return new Promise((resolve, reject) => {
      this.setFileProgress(file.name, 0, () => {
        S3UploadService.upload({
          file,
          onProgress: progress => this.onUploadProgress(file, progress),
          year: this.props.year,
          target: this.props.target,
        })
          .then((objectKey) => {
            resolve(objectKey);
          })
          .catch((ex) => {
            reject(ex);
          });
      });
    });
  }

  render() {
    const {
      error,
      files,
      isConfirmDeleteDisabled,
      isModalSaveDisabled,
      uploadsInProgress,
    } = this.state;
    const uploadedFiles = files.filter(file => file.uploaded);

    const uploadKeys = Object.keys(uploadsInProgress);
    const numUploadsInProgress = uploadKeys.length;
    const progressSum = uploadKeys.reduce(
      (sum, value) => sum + uploadsInProgress[value].progress,
      0,
    );
    const totalProgress = numUploadsInProgress > 0 ? progressSum / numUploadsInProgress : 0;

    const {
      frozen,
    } = this.props;

    return (
      <div className="upload-manager mb-5">
        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}
        {uploadedFiles.length > 0 && (
          <ul className="list-group">
            {uploadedFiles.map((file, index) => (
              <li className="list-group-item px-1 px-md-2 py-3" key={file.url}>
                <File
                  date={getFormattedDate(file.date_created)}
                  name={file.name}
                  onClickDelete={() => this.onClickDelete(index)}
                  onClickEdit={() => this.onClickEdit(index)}
                  size={bytesToSize(file.size)}
                  frozen={frozen}
                />
              </li>
            ))}
          </ul>
        )}
        {!frozen &&
        <Dropzone
          activeClassName=""
          className="upload-manager__dropzone p-5 my-4"
          disablePreview
          disabledClassName=""
          disabled={numUploadsInProgress > 0}
          onDrop={this.onDroppedFiles}
        >
          {numUploadsInProgress === 0 ? (
            <p className="m-0 text-center">Drag files here or click to upload</p>
          ) : (
            <ProgressBar progress={totalProgress} />
          )}
        </Dropzone>
        }
        <UploadModal
          isSaveDisabled={isModalSaveDisabled}
          onHidden={this.onUploadModalHidden}
          onShown={this.onUploadModalShown}
          onSubmit={this.onSubmitModal}
          ref={(ref) => {
            this.uploadModalEl = ref;
          }}
          setDescriptionRef={(ref) => {
            this.inputUploadDescriptionEl = ref;
          }}
        />
        <DeleteConfirmationModal
          isActionDisabled={isConfirmDeleteDisabled}
          onClickConfirm={this.onClickDeleteConfirm}
          ref={(ref) => {
            this.confirmDeleteModalEl = ref;
          }}
        />
      </div>
    );
  }
}

UploadManager.propTypes = {
  year: PropTypes.string.isRequired,
  target: PropTypes.string,
  frozen: PropTypes.bool.isRequired,
};

UploadManager.defaultProps = {
  target: null,
};

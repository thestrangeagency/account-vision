import Cookies from 'js-cookie';
import Evaporate from 'evaporate';
import SparkMD5 from 'spark-md5';
import createHash from 'sha.js';

import { checkStatus } from '../utils';

export default class S3UploadService {
  /*
  The only function that should be treated as public. Returns a promise
  which resolves with the key of the file uploaded to S3.
  */
  static upload({
    file, year, target, onProgress,
  }) {
    return S3UploadService.getParams({ file, year, target })
      .then(params => S3UploadService.postToS3({ file, onProgress, params }))
      .then(awsS3ObjectKey => S3UploadService.postToComplete(awsS3ObjectKey))
      .then(objectKey => objectKey);
  }

  static computeMd5(data) {
    return btoa(SparkMD5.ArrayBuffer.hash(data, true));
  }

  static computeSha256(data) {
    return createHash('sha256')
      .update(data, 'utf-8')
      .digest('hex');
  }

  static generateAmazonHeaders(acl, serverSideEncryption) {
    // Either of these may be null, so don't add them unless they exist:
    const headers = {};
    if (acl) headers['x-amz-acl'] = acl;
    if (serverSideEncryption) headers['x-amz-server-side-encryption'] = serverSideEncryption;
    return headers;
  }

  static getAwsV4Signature(signParams, signHeaders, stringToSign, signatureDateTime) {
    const formData = new FormData();
    formData.append('to_sign', stringToSign);
    formData.append('datetime', signatureDateTime);

    return fetch('/api/uploads/signature', {
      body: formData,
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken'),
      },
      method: 'POST',
    })
      .then(checkStatus)
      .then(response => response.text());
  }

  static getParams({ file, year, target }) {
    const formData = new FormData();
    formData.append('destination', 'uploads');
    formData.append('file_name', file.name);
    formData.append('file_size', file.size);
    formData.append('file_type', file.type);
    formData.append('year', year);
    formData.append('target', target);

    return fetch('/api/uploads/params', {
      body: formData,
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken'),
      },
      method: 'POST',
    })
      .then(checkStatus)
      .then(response => response.json());
  }

  static postToS3({ file, onProgress, params }) {
    const {
      object_key,
      access_key_id,
      region,
      bucket,
      cache_control,
      content_disposition,
      acl,
      server_side_encryption,
    } = params;

    return Evaporate.create({
      customAuthMethod: S3UploadService.getAwsV4Signature,
      aws_key: access_key_id,
      bucket,
      awsRegion: region,
      computeContentMd5: true,
      cryptoMd5Method: S3UploadService.computeMd5,
      cryptoHexEncodedHash256: S3UploadService.computeSha256,
      partSize: 20 * 1024 * 1024,
      logging: true,
      debug: true,
      allowS3ExistenceOptimization: true,
      s3FileCacheHoursAgo: 12,
      onlyRetryForSameFileName: true,
    }).then(evaporate =>
      evaporate.add({
        name: object_key,
        file,
        contentType: file.type,
        xAmzHeadersAtInitiate: S3UploadService.generateAmazonHeaders(acl, server_side_encryption),
        notSignedHeadersAtInitiate: {
          'Cache-Control': cache_control,
          'Content-Disposition': content_disposition,
        },
        progress: onProgress,
      }));
  }

  static postToComplete(objectKey) {
    const formData = new FormData();
    formData.append('object_key', objectKey);

    return fetch('/api/uploads/complete', {
      body: formData,
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken'),
      },
      method: 'POST',
    })
      .then(checkStatus)
      .then(() => objectKey);
  }
}

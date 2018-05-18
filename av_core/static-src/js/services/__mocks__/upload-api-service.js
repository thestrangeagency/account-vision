const files = [
  {
    url: 'http://0.0.0.0:5000/api/returns/2017/files/100/',
    s3_url:
      'https://tax-dev.s3.amazonaws.com/uploads/5/2eea131202ea43f592025f84ad5b9ba3?AWSAccessKeyId=AKIAINYXD4G744JQNAMA&Signature=5i2sbg845yq%2B4rfobAsFAgjwHkc%3D&Expires=1509308870',
    date_created: '2017-10-29T15:27:48.659937-04:00',
    date_modified: '2017-10-29T15:27:50.276490-04:00',
    name: 'package.json',
    type: 'application/json',
    size: 601,
    s3_key: 'uploads/5/2eea131202ea43f592025f84ad5b9ba3',
    s3_bucket: 'tax-dev',
    s3_region: 'us-west-2',
    description: '',
    uploaded: true,
    user: 'http://0.0.0.0:5000/api/users/5/',
    tax_return: 'http://0.0.0.0:5000/api/returns/5/',
  },
];

export default class UploadApiService {
  static getFiles() {
    return new Promise((resolve) => {
      process.nextTick(() => {
        resolve(files);
      });
    });
  }

  static deleteFile() {
    return new Promise((resolve) => {
      process.nextTick(() => {
        resolve();
      });
    });
  }
}

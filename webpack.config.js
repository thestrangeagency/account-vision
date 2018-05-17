const dev = require('./webpack.dev.js');
const prod = require('./webpack.prod.js');

if (process.env.DEBUG === '1') {
  console.log('starting dev build...');
  module.exports = dev;
} else {
  console.log('starting prod build...');
  module.exports = prod;
}

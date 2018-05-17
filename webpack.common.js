const path = require('path');

const baseDir = path.resolve(__dirname, 'av_core/static/js');

module.exports = {
  entry: './av_core/static-src/js/app.jsx',
  output: {
    path: baseDir,
    filename: 'bundle.js',
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: [
          'babel-loader',
        ],
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
};

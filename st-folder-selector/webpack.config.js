const path = require("path");

module.exports = {
  entry: "./index.js",
  output: {
    filename: "index.js",
    path: path.resolve(__dirname, "dist"),
  },
  module: {
    rules: [{ test: /\.jsx?$/, exclude: /node_modules/, loader: "babel-loader" }],
  },
  resolve: {
    extensions: [".js", ".jsx"],
  },
};

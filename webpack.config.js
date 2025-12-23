const path = require('path');

module.exports = {
  webpack: {
    configure: (webpackConfig, env) => {
      // Add a rule to handle the generated .docusaurus files
      webpackConfig.module.rules.push({
        test: /\.docusaurus\/.*\.js$/,
        type: 'javascript/auto',
        use: {
          loader: require.resolve('babel-loader'),
          options: {
            presets: [require.resolve('@docusaurus/core/lib/babel/preset')],
            sourceType: 'module',
          },
        },
      });

      // Handle the specific client-modules.js file
      webpackConfig.module.rules.push({
        test: /\.docusaurus\/client-modules\.js$/,
        type: 'javascript/auto',
        use: {
          loader: require.resolve('babel-loader'),
          options: {
            presets: [require.resolve('@docusaurus/core/lib/babel/preset')],
            sourceType: 'module',
          },
        },
      });

      // Add resolution for the .docusaurus directory
      webpackConfig.resolve = webpackConfig.resolve || {};
      webpackConfig.resolve.modules = [
        ...(webpackConfig.resolve.modules || []),
        path.resolve(__dirname, '.docusaurus'),
      ];

      return webpackConfig;
    },
  },
};
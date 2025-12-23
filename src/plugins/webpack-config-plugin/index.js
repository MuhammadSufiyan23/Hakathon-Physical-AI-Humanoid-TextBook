const path = require('path');

module.exports = function (context, options) {
  return {
    name: 'webpack-config-plugin',

    configureWebpack(config, isServer, utils) {
      // Add webpack configuration to handle ES module compatibility for generated files
      const newConfig = { ...config };

      // Add a new rule to handle the generated .docusaurus files that use ES module syntax
      newConfig.module.rules.push({
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

      // Add resolution for the .docusaurus directory
      newConfig.resolve = {
        ...newConfig.resolve,
        modules: [
          ...(newConfig.resolve.modules || []),
          path.resolve(__dirname, '../../../.docusaurus'),
        ],
      };

      return newConfig;
    },
  };
};
const webpackMerge = require('webpack-merge')
const prodEnv = require('./prod.env')

const { merge } = webpackMerge

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  PARKSTAY_URL: '"http://localhost:9191"'
})

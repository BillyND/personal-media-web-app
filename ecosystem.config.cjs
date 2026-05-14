module.exports = {
  apps: [
    {
      name: 'media-web',
      script: 'scripts/start-web.sh',
      interpreter: 'bash',
      autorestart: true,
      max_restarts: 10,
      env: {
        PORT: '8000'
      }
    },
    {
      name: 'media-worker',
      script: 'scripts/start-worker.sh',
      interpreter: 'bash',
      autorestart: true,
      max_restarts: 10
    }
  ]
}

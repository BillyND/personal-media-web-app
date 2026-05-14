async function refreshJobs() {
  const container = document.querySelector('[data-refresh-url]')
  if (!container) return
  const response = await fetch(container.dataset.refreshUrl, { credentials: 'same-origin' })
  if (response.ok) container.innerHTML = await response.text()
}

window.addEventListener('DOMContentLoaded', () => {
  refreshJobs()
  setInterval(refreshJobs, 3000)
})

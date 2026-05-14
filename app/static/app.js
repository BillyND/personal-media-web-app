const REFRESH_INTERVAL_MS = 3000
let refreshSequence = 0

async function refreshJobs() {
  const container = document.querySelector('[data-refresh-url]')
  if (!container) return
  if (document.activeElement && container.contains(document.activeElement)) return
  const sequence = ++refreshSequence
  try {
    const response = await fetch(container.dataset.refreshUrl, { credentials: 'same-origin' })
    if (!response.ok || sequence !== refreshSequence) return
    container.innerHTML = await response.text()
    bindJobsFragment(container)
  } catch (_error) {
    // Next interval retries automatically.
  }
}

function bindVoicePreference() {
  const languageSelect = document.querySelector('#tts-language')
  const voiceSelect = document.querySelector('#tts-voice')
  const sample = document.querySelector('[data-tts-sample]')
  if (!languageSelect || !voiceSelect) return

  const saveSelection = (select) => {
    try {
      localStorage.setItem(select.dataset.localStorageKey, select.value)
    } catch (_error) {}
  }

  const restoreSelection = (select) => {
    try {
      const saved = localStorage.getItem(select.dataset.localStorageKey)
      if (saved && [...select.options].some((option) => option.value === saved)) select.value = saved
    } catch (_error) {}
  }

  const syncVoices = () => {
    const languageId = languageSelect.value
    const options = [...voiceSelect.options]
    options.forEach((option) => {
      option.hidden = option.dataset.languageId !== languageId
    })
    if (voiceSelect.selectedOptions[0]?.hidden) {
      voiceSelect.value = options.find((option) => !option.hidden)?.value || ''
    }
    if (sample) sample.textContent = voiceSelect.selectedOptions[0]?.dataset.sampleText || ''
  }

  restoreSelection(languageSelect)
  restoreSelection(voiceSelect)
  syncVoices()

  languageSelect.addEventListener('change', () => {
    syncVoices()
    saveSelection(languageSelect)
    saveSelection(voiceSelect)
  })
  voiceSelect.addEventListener('change', () => {
    syncVoices()
    saveSelection(voiceSelect)
  })
}

function bindJobsFragment(root = document) {
  root.querySelectorAll('[data-jobs-page]').forEach((link) => {
    link.addEventListener('click', async (event) => {
      event.preventDefault()
      const container = document.querySelector('[data-refresh-url]')
      if (!container) return
      const page = link.dataset.jobsPage
      container.dataset.refreshUrl = `/jobs?page=${page}`
      const url = new URL(window.location.href)
      url.searchParams.set('page', page)
      window.history.replaceState({}, '', url)
      await refreshJobs()
    })
  })

  root.querySelectorAll('[data-text-preview-url]').forEach((preview) => {
    const details = preview.closest('details')
    if (!details || preview.dataset.loaded === 'true') return
    details.addEventListener('toggle', async () => {
      if (!details.open || preview.dataset.loaded === 'true') return
      try {
        const response = await fetch(preview.dataset.textPreviewUrl, { credentials: 'same-origin' })
        preview.textContent = response.ok ? await response.text() : 'Không tải được nội dung.'
      } catch (_error) {
        preview.textContent = 'Không tải được nội dung.'
      }
      preview.dataset.loaded = 'true'
    })
  })
}

window.addEventListener('DOMContentLoaded', () => {
  bindVoicePreference()
  bindJobsFragment()
  refreshJobs()
  setInterval(refreshJobs, REFRESH_INTERVAL_MS)
})

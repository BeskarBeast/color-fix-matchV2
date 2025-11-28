i18next
  .use(i18nextHttpBackend)
  .use(i18nextBrowserLanguageDetector)
  .init({
    fallbackLng: 'en', // default language
    debug: true,
    backend: {
      loadPath: './locales/{{lng}}/translation.json'
    }
  }, function(err, t) {
    if (err) return console.error(err);
    updateContent(); // set initial text
  });

// Function to update text on the page
function updateContent() {
  document.title = i18next.t('title');
  document.querySelector('h1').textContent = i18next.t('title');
  document.querySelector('h2').textContent = i18next.t('subtitle');
  document.querySelector('label[for="image"]').textContent = i18next.t('chooseImage');
  document.querySelector('label[for="cameraInput"]').textContent = i18next.t('takePicture');
  document.getElementById('detectBtn').textContent = i18next.t('detectColor');
  document.getElementById('drop-area').textContent = i18next.t('dragDrop');
  document.getElementById('placeholder').textContent = i18next.t('noImage');
}

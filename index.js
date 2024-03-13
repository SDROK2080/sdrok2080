function toggleSection(sectionId) {
  var section = document.getElementById(sectionId);

  if (section.style.display === "none") {
      section.style.display = "block";
  } else {
      section.style.display = "none";
  }
}
const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const port = 3000;

app.use(express.static('public'));

app.get('/getDirectoryContents', (req, res) => {
  const directoryPath = path.join(__dirname, 'public', 'research_articles');

  fs.readdir(directoryPath, (err, files) => {
    if (err) {
      console.error(err);
      res.status(500).send('Internal Server Error');
    } else {
      res.json({ files });
    }
  });
});

app.listen(port, () => {
  console.log(`Server is listening at http://localhost:${port}`);
});
function submitForm() {
  var contactForm = document.getElementById('contactForm');
  var responseMessage = document.getElementById('responseMessage');

  // Simulate sending email and show response
  var name = contactForm.elements.name.value;
  var email = contactForm.elements.email.value;
  var message = contactForm.elements.message.value;

  // Simulate an autoresponder message
  var autoresponderMessage = `Hello ${name},<br>Thank you for contacting us! We have received your message:<br><em>${message}</em><br>We will get back to you at ${email}.`;

  // Display the autoresponder message
  responseMessage.innerHTML = autoresponderMessage;

  // Clear the form (simulate form submission)
  contactForm.reset();
}
function search() {
  const query = document.getElementById('searchInput').value;
  const resultsContainer = document.getElementById('resultsContainer');

  // Dummy search results (replace with actual search implementation)
  // Display results
  resultsContainer.innerHTML = "";
  dummyResults.forEach(result => {
    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';
    resultItem.textContent = result;
    resultsContainer.appendChild(resultItem);
  });
}
function search() {
  const query = document.getElementById('searchInput').value;
  const resultsContainer = document.getElementById('resultsContainer');

  // Dummy search results (replace with actual search implementation)
  // Display results
  resultsContainer.innerHTML = "";
  dummyResults.forEach(result => {
    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';
    resultItem.textContent = result;
    resultsContainer.appendChild(resultItem);
  });
}
function openFolder(folderName) {
  alert("Opened folder: " + folderName);
}

document.querySelectorAll('.file').forEach(file => {
  file.addEventListener('click', () => {
    const fileType = file.getAttribute('data-type');
    alert("Opened file of type: " + fileType);
  });
});










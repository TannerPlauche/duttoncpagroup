const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, 'public')));

// Explicit route mappings for service pages
const routeMap = {
  '/griffin/bookkeeping': 'griffin-bookkeeping.html',
  '/griffin/business-services': 'griffin-business-services.html',
  '/griffin/tax-planning': 'griffin-tax-planning.html',
  '/griffin/taxes': 'griffin-taxes.html',
  '/griffin_accounting/about': 'griffin_accounting-about.html'
};

// Handle mapped routes
Object.keys(routeMap).forEach(route => {
  app.get(route, (req, res) => {
    res.sendFile(path.join(__dirname, 'public', routeMap[route]));
  });
});

// Fallback for other routes
app.use((req, res) => {
  const filePath = path.join(__dirname, 'public', req.path);

  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    res.sendFile(filePath);
  } else if (fs.existsSync(filePath + '.html')) {
    res.sendFile(filePath + '.html');
  } else {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
  }
});

app.listen(PORT, () => {
  console.log(`\n🚀 Server is running!`);
  console.log(`📍 Local: http://localhost:${PORT}`);
  console.log(`📁 Serving files from: ${path.join(__dirname, 'public')}\n`);
});

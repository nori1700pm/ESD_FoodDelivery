const express = require('express');
const swaggerUi = require('swagger-ui-express');
const fs = require('fs');
const path = require('path');

const app = express();

const paths = [];

// Serve Swagger documentation for all services
const swaggerDocsPath = path.join(__dirname, 'swaggerDocs');
const swaggerFiles = fs.readdirSync(swaggerDocsPath);

swaggerFiles.forEach((file) => {
  if (file.endsWith('.json')) {
    const serviceName = file.replace('.json', '');
    const swaggerJson = require(path.join(swaggerDocsPath, file));

    // Create a middleware function that captures the swaggerJson
    const serveSwagger = (req, res, next) => {
      swaggerUi.setup(swaggerJson)(req, res, next);
    };

    // Create a route for each service's Swagger documentation
    const routePath = `/api-docs/${serviceName}`;
    app.use(routePath, swaggerUi.serve, serveSwagger);
    paths.push(routePath);
    console.log(`Swagger docs for ${serviceName} are available at ${routePath}`);
  }
});

// Add a home page route to list all paths
app.get('/api-docs/', (req, res) => {
  res.send(`
    <h1>Available Swagger Documentation</h1>
    <ul>
      ${paths.map((path) => `<li><a href="${path}">${path}</a></li>`).join('')}
    </ul>
  `);
});

// Example of health check route
app.get('/health', (req, res) => {
  res.send('Service is healthy');
});

const port = process.env.PORT || 6008;
app.listen(port, () => {
  console.log(`Swagger docs server is running on port ${port}`);
});
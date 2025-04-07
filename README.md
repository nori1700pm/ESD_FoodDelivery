# NomNomGo!
GitHub Repository: 
https://github.com/nori1700pm/ESD_FoodDelivery.git

# Description
NomNomGo! is a food delivery microservice application developed using Vue 3 and Vite framework, Docker, Python Flask, Firebase and Outsystems. This application consists of both a customer interface and a driver interface to handle scenarios from both perspectives.

# Prerequisites
Node.js (version 14 or later)

# Running locally
**Step 1: Clone the repository and run frontend**

1)  ```git clone https://github.com/nori1700pm/ESD_FoodDelivery.git```
2)  ```cd ESD_FoodDelivery```
3)  ```cd frontend```
4)  ```npm install```
5) ```npm run dev```

**Step 2: Run the backend**

5) ```cd ESD_FoodDelivery```
6) ```docker-compose up --build```

After doing these two steps the application will be running on http://localhost:5173/

# Credentials

### Customer Test Account (If required)
> **Note:** This is a test account for feature demonstration purposes only.  
> To test the email functionality for customer account, 
> please sign up using your own email address.

- **Email:** `changeadvisoryboard.esm.g10@gmail.com`  
- **Password:** `123123`

### Driver Test Account (Required)
> **Note:** The driver test account is needed to test driver functionalities such as rejecting assigned orders. Due to low hiring period, applications for new driver accounts are not accepted.

- **Email:** `jewel@driver.com`  
- **Password:** `123123`

# Swagger Documentation

**To run:**

1)  ```cd to ESD_FoodDelivery folder```
2)  ```cd swagger```
3)  ```npm install express swagger-ui-express```
4)  ```node swagger.js```

After doing this you can view the swagger documentation on http://localhost:6008/api-docs/

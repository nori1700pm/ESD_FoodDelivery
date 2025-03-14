<template>
  <div>
    <h1>{{ message }}</h1>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      message: "Loading..."
    };
  },
  mounted() {
    axios.get("http://localhost:5000/api/data")
      .then(response => {
        this.message = response.data.message;
      })
      .catch(error => {
        console.error("Error fetching data:", error);
      });
  }
};
</script>

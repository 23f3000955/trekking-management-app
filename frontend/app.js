const { createApp } = Vue

createApp({
    data() {
        return {
            currentPage: "home",
            name: "",
            email: "",
            password: "",
            message: ""
        }
    },

    methods: {
        goTo(page) {
            this.currentPage = page
            this.message = ""
        },

        async registerUser() {
            try {
                const response = await fetch("http://127.0.0.1:5000/register", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        name: this.name,
                        email: this.email,
                        password: this.password
                    })
                })

                const data = await response.json()
                this.message = data.message
            } catch (error) {
                this.message = "Connection error"
            }
        },

        async loginUser() {
            try {
                const response = await fetch("http://127.0.0.1:5000/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        email: this.email,
                        password: this.password
                    })
                })

                const data = await response.json()
                this.message = data.message
            } catch (error) {
                this.message = "Connection error"
            }
        }
    }
}).mount("#app")
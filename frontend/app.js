const { createApp } = Vue

createApp({


data() {

    return {

        currentPage: "home",

        // Authentication
        name: "",
        email: "",
        password: "",
        message: "",
        userRole: "",
        expectedRole: "",

        // Admin Dashboard
        adminPage: "dashboard",

        // Trek
        trekName: "",
        location: "",
        difficulty: "",
        duration: "",
        availableSlots: "",

        // Dashboard
        totalTreks: 0,

        // Trek List
        treks: [],
        editingTrek: false,
        editingTrekId: null,

        // Staff
        staffName: "",
        staffEmail: "",
        staffPassword: "",

        staffs: [],

        editingStaff: false,
        editingStaffId: null,

        // Assign Staff
        selectedTreks: {},

        // Dashboard Users
        users: [],

        // Bookings
        bookings: [],

        // Search
        searchText: "",
        searchResults: [],

        chart: null

    }

},

    methods: {

    goTo(page) {

    console.log("goTo called with:", page)

    this.currentPage = page
    this.message = ""

    if (page === "user-login") {
        this.expectedRole = "user"
    }

    else if (page === "staff-login") {
        this.expectedRole = "staff"
    }

    else if (page === "admin-login") {
        this.expectedRole = "admin"
    }

},
     
goToAdmin(page) {

    this.adminPage = page
    this.message = ""

    if (page === "dashboard") {

        this.loadDashboard()

    }

    else if (page === "manage-treks") {

        this.loadTreks()

    }

    else if (page === "add-staff") {

        this.loadStaff()

    }

    else if (page === "assign-staff") {

        this.loadStaff()
        this.loadTreks()

    }

    else if (page === "bookings") {

        this.loadBookings()

    }

    else if (page === "reports") {

        this.loadDashboard()

    }

},
drawChart() {

    const canvas = document.getElementById("statsChart")

    if (!canvas) {

        return

    }

    if (this.chart) {

        this.chart.destroy()

    }

    this.chart = new Chart(canvas, {

        type: "pie",

        data: {

            labels: [

                "Treks",
                "Users",
                "Staff",
                "Bookings"

            ],

            datasets: [

                {

                    data: [

                        this.totalTreks,
                        this.users.length,
                        this.staffs.length,
                        this.bookings.length

                    ],

                    backgroundColor: [

                        "#0d6efd",
                        "#198754",
                        "#ffc107",
                        "#dc3545"

                    ]

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: true,

            plugins: {

                legend: {

                    position: "bottom"

                }

            }

        }

    })

},
      async loadDashboard() {

    try {

        const trekResponse = await fetch(
            "http://127.0.0.1:5000/treks"
        )

        const trekData = await trekResponse.json()

        this.totalTreks = trekData.length

        await this.loadUsers()

        await this.loadStaff()

        await this.loadBookings()

        this.$nextTick(() => {

            this.drawChart()

        })

    }

    catch (error) {

        console.log(error)

    }

},
async loadUsers() {

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/users",
            {
                credentials: "include"
            }
        )

        const data = await response.json()

        if (response.ok) {

            this.users = data

        }

        else {

            this.message = data.message

        }

    }

    catch (error) {

        this.message = "Connection error"

    }

},

async toggleUserStatus(userId) {

    try {

        const response = await fetch(

            `http://127.0.0.1:5000/toggle_user_status/${userId}`,

            {

                method: "PUT",
                credentials: "include"

            }

        )

        const data = await response.json()

        this.message = data.message

        if (response.ok) {

            await this.loadUsers()

            await this.loadStaff()

        }

    }

    catch (error) {

        this.message = "Connection error"

    }

},



        async loadTreks() {

            try {

                const response = await fetch("http://127.0.0.1:5000/treks")

                const data = await response.json()

                this.treks = data

            }

            catch (error) {

                console.log(error)

            }

        },

        async registerUser() {

            if (

                this.name.trim() === "" ||
                this.email.trim() === "" ||
                this.password.trim() === ""

            ) {

                this.message = "Please fill all fields"
                return

            }

            try {

                const response = await fetch("http://127.0.0.1:5000/register", {

                    method: "POST",
                    credentials: "include",

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

            }

            catch (error) {

                this.message = "Connection error"

            }

        },

       
async loadStaff() {

    try {

        const response = await fetch(

            "http://127.0.0.1:5000/staffs",

            {

                credentials: "include"

            }

        )

        const data = await response.json()

        this.staffs = data

    }

    catch (error) {

        console.log(error)

    }

},


editStaff(staff) {

    this.editingStaff = true

    this.editingStaffId = staff.id

    this.staffName = staff.name

    this.staffEmail = staff.email

    this.staffPassword = ""

},

async updateStaff() {

    try {

        const response = await fetch(

            `http://127.0.0.1:5000/update_staff/${this.editingStaffId}`,

            {

                method: "PUT",

                credentials: "include",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify({

                    name: this.staffName,

                    email: this.staffEmail,

                    password: this.staffPassword

                })

            }

        )

        const data = await response.json()

        this.message = data.message

        if (response.ok) {

            this.editingStaff = false

            this.editingStaffId = null

            this.staffName = ""

            this.staffEmail = ""

            this.staffPassword = ""

            await this.loadStaff()

        }

    }

    catch (error) {

        this.message = "Connection error"

    }

},



async deleteStaff(id) {

    const confirmDelete = confirm("Delete this staff member?")

    if (!confirmDelete) {

        return

    }

    try {

        const response = await fetch(

            `http://127.0.0.1:5000/delete_staff/${id}`,

            {

                method: "DELETE",

                credentials: "include"

            }

        )

        const data = await response.json()

        this.message = data.message

        if (response.ok) {

            await this.loadStaff()

        }

    }

    catch (error) {

        this.message = "Connection error"

    }

},

async assignStaff(staffId) {

    const trekId = this.selectedTreks[staffId]

    if (!trekId) {

        this.message = "Please select a trek"
        return

    }

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/assign_staff",
            {

                method: "POST",
                credentials: "include",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    staff_id: staffId,
                    trek_id: trekId

                })

            }
        )

        const data = await response.json()

        this.message = data.message

        if (response.ok) {

            await this.loadStaff()
            await this.loadTreks()

        }

    }

    catch (error) {

        this.message = "Connection error"

    }

},

async unassignStaff(trekId) {

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/unassign_staff",
            {

                method: "POST",
                credentials: "include",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    trek_id: trekId

                })

            }
        )

        const data = await response.json()

        this.message = data.message

        if (response.ok) {

            await this.loadStaff()
            await this.loadTreks()

        }

    }

    catch (error) {

        this.message = "Connection error"

    }

},







async loginUser() {

    if (

        this.email.trim() === "" ||
        this.password.trim() === ""

    ) {

        this.message = "Please enter email and password"
        return

    }

    try {

        const response = await fetch("http://127.0.0.1:5000/login", {

            method: "POST",
            credentials: "include",

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

        if (data.message === "Login successful") {

            if (data.role !== this.expectedRole) {

                this.message =
                    `This account is a ${data.role} account. Please use the ${data.role.charAt(0).toUpperCase() + data.role.slice(1)} Login page.`

                return

            }

            this.userRole = data.role

            if (data.role === "user") {

                this.currentPage = "user-dashboard"

            }

            else if (data.role === "admin") {

                this.currentPage = "admin-dashboard"
                this.adminPage = "dashboard"

                this.loadDashboard()

            }

            else if (data.role === "staff") {

                this.currentPage = "staff-dashboard"

            }

        }

    }

    catch (error) {

        this.message = "Connection error"

    }

},


async addTrek() {

    alert("Before Fetch\ncurrentPage = " + this.currentPage + "\nadminPage = " + this.adminPage)

    if (

        this.trekName.trim() === "" ||
        this.location.trim() === "" ||
        this.difficulty.trim() === "" ||
        this.duration === "" ||
        this.availableSlots === ""

    ) {

        this.message = "Please fill all fields"
        return

    }

    try {

        const response = await fetch("http://127.0.0.1:5000/add_trek", {

            method: "POST",
            credentials: "include",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                trek_name: this.trekName,
                location: this.location,
                difficulty: this.difficulty,
                duration: this.duration,
                available_slots: this.availableSlots

            })

        })

        alert("After Fetch\ncurrentPage = " + this.currentPage + "\nadminPage = " + this.adminPage)

        const data = await response.json()

        this.message = data.message

        if (response.ok) {

            this.trekName = ""
            this.location = ""
            this.difficulty = ""
            this.duration = ""
            this.availableSlots = ""

            this.currentPage = "admin-dashboard"
            this.adminPage = "add-trek"

            alert("After Setting\ncurrentPage = " + this.currentPage + "\nadminPage = " + this.adminPage)

            await this.loadDashboard()
            await this.loadTreks()

        }

    }

    catch (error) {

        alert(error)
        this.message = "Connection error"

    }

},



async searchData() {

    if (this.searchText.trim() === "") {

        this.searchResults = []
        return

    }

    try {

        const response = await fetch(

            `http://127.0.0.1:5000/search?q=${encodeURIComponent(this.searchText)}`,

            {

                credentials: "include"

            }

        )

        const data = await response.json()

        if (response.ok) {

            this.searchResults = data

        }

        else {

            this.message = data.message

        }

    }

    catch (error) {

        this.message = "Connection error"

    }

},


async updateTrek() {

    try {

        const response = await fetch(
            `http://127.0.0.1:5000/update_trek/${this.editingTrekId}`,
            {
                method: "PUT",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    trek_name: this.trekName,
                    location: this.location,
                    difficulty: this.difficulty,
                    duration: this.duration,
                    available_slots: this.availableSlots
                })
            }
        )

        const data = await response.json()

        this.message = data.message

        if (response.ok) {

            this.editingTrek = false
            this.editingTrekId = null

            this.trekName = ""
            this.location = ""
            this.difficulty = ""
            this.duration = ""
            this.availableSlots = ""

            await this.loadTreks()
            await this.loadDashboard()

            this.adminPage = "manage-treks"

        }

    }

    catch (error) {

        this.message = "Connection error"

    }

},





editTrek(trek) {

    this.editingTrek = true
    this.editingTrekId = trek.id

    this.trekName = trek.name
    this.location = trek.location
    this.difficulty = trek.difficulty
    this.duration = trek.duration
    this.availableSlots = trek.slots

    this.adminPage = "add-trek"

},


async addStaff() {

    if (

        this.staffName.trim() === "" ||
        this.staffEmail.trim() === "" ||
        this.staffPassword.trim() === ""

    ) {

        this.message = "Please fill all fields"
        return

    }

    try {

        const response = await fetch(

            "http://127.0.0.1:5000/add_staff",

            {

                method: "POST",
                credentials: "include",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify({

                    name: this.staffName,
                    email: this.staffEmail,
                    password: this.staffPassword

                })

            }

        )

        const data = await response.json()

        this.message = data.message

        if (response.ok) {

            this.staffName = ""
            this.staffEmail = ""
            this.staffPassword = ""

            await this.loadStaff()

        }

    }

    catch (error) {

        this.message = "Connection error"

    }

},


        async deleteTrek(id) {

            const confirmDelete = confirm("Are you sure you want to delete this trek?")

            if (!confirmDelete) {
                return
            }

            try {

                const response = await fetch(
                    `http://127.0.0.1:5000/delete_trek/${id}`,
                    {
                        method: "DELETE",
                        credentials: "include"
                    }
                )

                const data = await response.json()

                this.message = data.message

                if (response.ok) {

                    await this.loadTreks()
                    await this.loadDashboard()

                    this.adminPage = "manage-treks"

                }

            }

            catch (error) {

                this.message = "Connection error"

            }

        }

    }

}).mount("#app")
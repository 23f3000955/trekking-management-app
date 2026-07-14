const { createApp } = Vue

createApp({


data() {

    console.log("Vue Created")

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

        chart: null,

       // ================= USER DASHBOARD =================

userPage: "dashboard",

availableTreks: [],

myBookings: [],

userTotalBookings: 0,

userActiveTreks: 0,

userCompletedTreks: 0,

editingUserProfile: false,
// User Search
userSearchText: "",
filterLocation: "",
filterDifficulty: "",
filterDuration: "",
userSearchResults: [],
userSearchDone: false,
// Export
exportQueued: false,
exportTaskId: "",
exportStatus: "",
// Admin Jobs
adminJobMsg: "",
// User Profile
userProfile: {
    id: "",
    name: "",
    email: "",
    contact: "",
     address: "",
    active: true,
},


// ================= STAFF DASHBOARD =================

staffPage: "dashboard",

assignedTreks: [],

participants: [],

staffAssignedTreks: 0,

openTreks: 0,

completedTreks: 0,

totalParticipants: 0,

staffProfile: {

    id: "",

    name: "",

    email: "",

    contact: "",

    address: "",

    experience: "",

    active: true,

    treks: []

}

    }

},
computed: {
    uniqueLocations() {
        return [...new Set(this.userSearchResults.map(t => t.location))].sort()
    },
    uniqueDifficulties() {
        return [...new Set(this.userSearchResults.map(t => t.difficulty))].sort()
    },
    uniqueDurations() {
        return [...new Set(this.userSearchResults.map(t => t.duration))].sort((a, b) => a - b)
    },
    filteredSearchResults() {
        return this.userSearchResults.filter(trek => {
            const matchesLocation = !this.filterLocation ||
                trek.location.toLowerCase() === this.filterLocation.toLowerCase()
            const matchesDifficulty = !this.filterDifficulty ||
                trek.difficulty.toLowerCase() === this.filterDifficulty.toLowerCase()
            const matchesDuration = !this.filterDuration ||
                String(trek.duration) === String(this.filterDuration)
            return matchesLocation && matchesDifficulty && matchesDuration
        })
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


goToStaff(page) {

    this.staffPage = page

    this.message = ""

    if (page === "dashboard") {

        this.loadStaffDashboard()

    }

    else if (page === "profile") {

        this.loadStaffProfile()

    }

    else if (page === "assigned-treks") {

        this.loadStaffDashboard()

    }

    else if (page === "participants") {

        this.loadParticipants()

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


async loadStaffDashboard() {

    try {

        const response = await fetch(

            "http://127.0.0.1:5000/staff/assigned_treks",

            {

                credentials: "include"

            }

        )

        const data = await response.json()

        if (!response.ok) {

            this.message = data.message

            return

        }

        this.assignedTreks = data

        this.staffAssignedTreks = data.length

        this.openTreks = data.filter(
            trek => trek.status === "Open"
        ).length

        this.completedTreks = data.filter(
            trek => trek.status === "Completed"
        ).length

        this.totalParticipants = data.reduce(

            (total, trek) => total + trek.participants,

            0

        )

    }

    catch (error) {

        this.message = "Connection error"

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

    this.staffContact = staff.contact

    this.staffAddress = staff.address

    this.staffExperience = staff.experience

    this.staffEmergencyContact = staff.emergency_contact

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

                    password: this.staffPassword,

                    contact: this.staffContact,

                    address: this.staffAddress,

                    experience: this.staffExperience,

                    emergency_contact: this.staffEmergencyContact

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

            this.staffContact = ""

            this.staffAddress = ""

            this.staffExperience = ""

            this.staffEmergencyContact = ""

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

async loadUserTreks() {

    try {

        const response = await fetch(

            "http://127.0.0.1:5000/user/treks",

            {

                credentials: "include"

            }

        )

        const data = await response.json()

        if (response.ok) {

            this.availableTreks = data

        }

        else {

            this.message = data.message

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

        const response = await fetch(

            "http://127.0.0.1:5000/login",

            {

                method: "POST",

                credentials: "include",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify({

                    email: this.email,
                    password: this.password

                })

            }

        )

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

                this.userPage = "dashboard"

                await this.loadUserTreks()

            }

            else if (data.role === "admin") {

                this.currentPage = "admin-dashboard"

                this.adminPage = "dashboard"

                await this.loadDashboard()

            }

            else if (data.role === "staff") {

                this.currentPage = "staff-dashboard"

                this.staffPage = "dashboard"

                await this.loadStaffDashboard()

            }

        }

    }

    catch (error) {

        console.log(error)

        this.message = "Connection error"

    }

},


async addTrek() {

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

            await this.loadDashboard()
            await this.loadTreks()

        }

    }

    catch (error) {

        console.log(error)
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


async loadStaffProfile() {

    try {

        const response = await fetch(

            "http://127.0.0.1:5000/staff/profile",

            {

                credentials: "include"

            }

        )

        const data = await response.json()

        if (response.ok) {

            this.staffProfile = data

        }

        else {

            this.message = data.message

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



async loadBookings() {

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/bookings",
            {
                credentials: "include"
            }
        )

        const data = await response.json()

        if (response.ok) {

            this.bookings = data

        }

        else {

            this.message = data.message

        }

    }

    catch (error) {

        console.log(error)

    }

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
                    password: this.staffPassword,
                    contact: this.staffContact,
                    address: this.staffAddress,
                    experience: this.staffExperience,
                    emergency_contact: this.staffEmergencyContact

                })

            }

        )

        const data = await response.json()

        this.message = data.message

        if (response.ok) {

            this.staffName = ""
            this.staffEmail = ""
            this.staffPassword = ""
            this.staffContact = ""
            this.staffAddress = ""
            this.staffExperience = ""
            this.staffEmergencyContact = ""

            await this.loadStaff()

        }

    }

    catch (error) {

        this.message = "Connection error"

    }

},

async bookTrek(trekId) {

    try {

        const response = await fetch(

            "http://127.0.0.1:5000/book_trek",

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

        alert(data.message)

        if (response.ok) {

            await this.loadUserTreks()

        }

    }

    catch (error) {

        console.log(error)

        this.message = "Connection error"

    }

},

async startTrek(trek) {

    trek.status = "Started"

    await this.updateAssignedTrek(trek)

    await this.loadStaffDashboard()

},
async completeTrek(trek) {

    trek.status = "Completed"

    await this.updateAssignedTrek(trek)

    await this.loadStaffDashboard()

},

async loadParticipants() {

    try {

        const response = await fetch(

            "http://127.0.0.1:5000/staff/participants",

            {

                credentials: "include"

            }

        )

        const data = await response.json()

        if (response.ok) {

            this.participants = data

        }

        else {

            this.message = data.message

        }

    }

    catch (error) {

        console.log(error)

        this.message = "Connection error"

    }

},

async updateAssignedTrek(trek) {

    try {

        const response = await fetch(

            `http://127.0.0.1:5000/staff/update_trek/${trek.id}`,

            {

                method: "PUT",

                credentials: "include",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify({

                    slots: trek.slots,
                    status: trek.status

                })

            }

        )

        const data = await response.json()

        this.message = data.message

        if (response.ok) {

            await this.loadStaffDashboard()

        }

    }

    catch (error) {

        console.log(error)

        this.message = "Connection error"

    }

},
async loadUserDashboard() {

    try {

        const response = await fetch(

            "http://127.0.0.1:5000/user/dashboard",

            {

                credentials: "include"

            }

        )

        const data = await response.json()

        if (response.ok) {

            this.userTotalBookings = data.total_bookings

            this.userActiveTreks = data.active_treks

            this.userCompletedTreks = data.completed_treks

        }

        else {

            this.message = data.message

        }

    }

    catch (error) {

        console.log(error)

        this.message = "Connection error"

    }

},


async loadMyBookings() {

    try {

        const response = await fetch(

            "http://127.0.0.1:5000/user/bookings",

            {

                credentials: "include"

            }

        )

        const data = await response.json()

        if (response.ok) {

            this.myBookings = data

        }

        else {

            this.message = data.message

        }

    }

    catch (error) {

        console.log(error)

        this.message = "Connection error"

    }

},
async loadUserProfile() {

    try {

        const response = await fetch(

            "http://127.0.0.1:5000/user/profile",

            {

                credentials: "include"

            }

        )

        const data = await response.json()

        if (response.ok) {

            this.userProfile = data

        }

        else {

            this.message = data.message

        }

    }

    catch (error) {

        console.log(error)

        this.message = "Connection error"

    }

},
async updateUserProfile() {

    try {

        const response = await fetch(

            "http://127.0.0.1:5000/user/profile",

            {

                method: "PUT",

                credentials: "include",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify({

                    name: this.userProfile.name,

                    email: this.userProfile.email,

                    contact: this.userProfile.contact,

                    address: this.userProfile.address

                })

            }

        )

        const data = await response.json()

        this.message = data.message

        if (response.ok) {

            this.editingUserProfile = false

            await this.loadUserProfile()

            alert("Profile updated successfully")

        }

        else {

            alert(data.message)

        }

    }

    catch (error) {

        console.log(error)

        this.message = "Connection error"

        alert("Connection error")

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

               },
        async searchUserTreks() {
            this.userSearchDone = false
            try {
                const params = new URLSearchParams()
                if (this.userSearchText.trim()) params.append("q", this.userSearchText.trim())
                const response = await fetch(
                    `http://127.0.0.1:5000/user/search?${params.toString()}`,
                    { credentials: "include" }
                )
                const data = await response.json()
                if (response.ok) {
                    this.userSearchResults = data
                    this.filterLocation   = ""
                    this.filterDifficulty = ""
                    this.filterDuration   = ""
                } else {
                    this.message = data.message
                }
            } catch (error) {
                this.message = "Connection error"
            }
             this.userSearchDone = true
        },
        async triggerAsyncExport() {
            this.exportQueued = true
            this.exportStatus = ""
            try {
                const response = await fetch(
                    "http://127.0.0.1:5000/user/export_bookings_async",
                    { method: "POST", credentials: "include" }
                )
                const data = await response.json()
                this.message = data.message
                this.exportTaskId = data.task_id || ""
            } catch (error) {
                this.message = "Connection error"
            }
            this.exportQueued = false
        },
        async pollExportStatus() {
            if (!this.exportTaskId) return
            try {
                const response = await fetch(
                    `http://127.0.0.1:5000/user/export_status/${this.exportTaskId}`,
                    { credentials: "include" }
                )
                const data = await response.json()
                this.exportStatus = data.status
            } catch (error) {
                this.message = "Connection error"
            }
        },
        async triggerAdminJob(type) {
            const url = type === "reminders"
                ? "http://127.0.0.1:5000/admin/trigger_reminders"
                : "http://127.0.0.1:5000/admin/trigger_monthly_report"
            try {
                const response = await fetch(url, { method: "POST",
                    credentials: "include"
                })
                const data = await response.json()
                this.adminJobMsg = data.message
                setTimeout(() => { this.adminJobMsg = "" }, 4000)
            } catch (error) {
                this.adminJobMsg = "Connection error"
            }
        },
        async logout() {
            try {
                await fetch("http://127.0.0.1:5000/logout", {
                    method: "POST",
                    credentials: "include"
                })
            } catch (error) {
                console.log(error)
            }
            this.currentPage = "home"
            this.userRole = ""
            this.message = ""
        }
    },
    async mounted() {
        try {
            const response = await fetch("http://127.0.0.1:5000/check_login", {
                credentials: "include"
            })
            const data = await response.json()
            if (data.logged_in) {
                this.userRole = data.role
                if (data.role === "user") {
                    this.currentPage = "user-dashboard"
                    this.userPage = "dashboard"
                    await this.loadUserDashboard()
                    await this.loadUserTreks()
                    await this.loadMyBookings()
                    await this.loadUserProfile()
                } else if (data.role === "admin") {   this.currentPage = "admin-dashboard"
                    this.adminPage = "dashboard"
                    await this.loadDashboard()
                } else if (data.role === "staff") {
                    this.currentPage = "staff-dashboard"
                    this.staffPage = "dashboard"
                    await this.loadStaffDashboard()
                }
            }
        } catch (error) {
            console.log(error)
        }
    }
}).mount("#app")
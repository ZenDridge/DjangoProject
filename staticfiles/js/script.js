document.addEventListener("DOMContentLoaded", () => {
    /* About Pop out Functionality */
    const modal = document.getElementById("modal");
    const openModalBtn = document.getElementById("openModal");
    const closeModalBtn = document.getElementById("closeModal");

    // Open modal function
    function openModal() {
        const modalContent = modal.querySelector('.modal-content');
        modal.style.display = 'flex'; // Show modal
        modalContent.classList.add('show-scroll'); // Enable scroll effect

        // Fade-in the content
        setTimeout(() => {
            modalContent.style.opacity = 1;
        }, 200);
    }

    // Close modal function
    function closeModal() {
        const modalContent = modal.querySelector('.modal-content');
        modal.style.display = 'none'; // Hide modal
        modalContent.classList.remove('show-scroll'); // Disable scroll effect
    }

    // Open modal event
    openModalBtn.addEventListener("click", (event) => {
        event.preventDefault();
        openModal();
    });

    // Close modal event
    closeModalBtn.addEventListener("click", closeModal);

    // Close modal if clicked outside of modal content
    window.addEventListener("click", (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });
});

/* Contact Button Functionality */
const contactButton = document.querySelector('.contact-button');
let hideIconsTimeout; // Variable to store the timeout ID

// Toggle the 'active' class on click
contactButton.addEventListener('click', function (event) {
    event.stopPropagation(); // Prevent event bubbling
    this.classList.toggle('active'); // Toggle the 'active' class
    clearTimeout(hideIconsTimeout); // Cancel any existing timeout to hide the icons
});

// Hide icons 3 seconds after mouse leaves the contact button
contactButton.addEventListener('mouseleave', function () {
    hideIconsTimeout = setTimeout(() => {
        contactButton.classList.remove('active'); // Remove the 'active' class
    }, 500); // Delay for 0.5 second
});

// Optional: Cancel hiding if the mouse re-enters within the timeout period
contactButton.addEventListener('mouseenter', function () {
    clearTimeout(hideIconsTimeout); // Cancel the timeout to keep icons visible
});

/* Event Cards Interaction */
const eventCards = document.querySelectorAll('.event-card');

// Apply event listeners to each card
eventCards.forEach(card => {
    card.addEventListener('mouseenter', () => {
        // Dim all other cards when one card is hovered
        eventCards.forEach(otherCard => {
            if (otherCard !== card) {
                otherCard.style.opacity = '0.5'; // Dim the other cards
                otherCard.style.filter = 'brightness(0.5)'; // Optional: Apply a dimming effect
            }
        });
    });

    card.addEventListener('mouseleave', () => {
        // Reset all cards when the hover ends
        eventCards.forEach(otherCard => {
            otherCard.style.opacity = '1'; // Reset opacity
            otherCard.style.filter = ''; // Reset filter
        });
    });
});

/* Officer Carousel Functionality */
const officerContainer = document.querySelector('.officer-container');
const forwardButton = document.getElementById('forward');
const backwardButton = document.getElementById('backward');

// Define the display pattern (how many officers to show at each step)
const imageDisplayPattern = [3, 2, 2, 3, 2, 3];
const totalOfficers = 15; // Total number of officers (1-15)
let currentStep = 0; // Track the current step in the display pattern
let currentOfficerIndex = 0; // Track the index of the first officer to display

// Function to update the officer display
function updateView() {
    const officerFrames = document.querySelectorAll('.officer-frame');
    const imagesToShow = imageDisplayPattern[currentStep]; // Number of images to show in this step

    // Hide all frames initially
    officerFrames.forEach(frame => frame.style.display = 'none');

    // Show the required number of frames based on the current step and index
    for (let i = 0; i < imagesToShow; i++) {
        const indexToShow = currentOfficerIndex + i; // Calculate which officer to show
        if (indexToShow < totalOfficers) {
            officerFrames[indexToShow].style.display = 'block'; // Show the officer frame
        }
    }

    // Update the button states
    forwardButton.disabled = currentOfficerIndex + imagesToShow >= totalOfficers; // Disable forward if no more images to show
    backwardButton.disabled = currentOfficerIndex <= 0; // Disable backward if already at the first step
}

// Event listener for Forward button (Right arrow)
forwardButton.addEventListener('click', () => {
    // Move forward only if there are more images to show
    if (currentOfficerIndex + imageDisplayPattern[currentStep] < totalOfficers) {
        currentOfficerIndex += imageDisplayPattern[currentStep]; // Move forward by the number of images in the current step
        currentStep = Math.min(currentStep + 1, imageDisplayPattern.length - 1); // Move to the next step but not beyond the last step
        updateView(); // Update the view with the next images
    }
});

// Event listener for Backward button (Left arrow)
backwardButton.addEventListener('click', () => {
    // Move backward only if there are previous images to show
    if (currentStep > 0) {
        currentStep--; // Move to the previous step
        currentOfficerIndex -= imageDisplayPattern[currentStep]; // Move backward by the number of images in the previous step
        updateView(); // Update the view with the previous images
    }
});

// Initialize the view
updateView();

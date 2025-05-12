
function openPlaceDetails(data) {
    const modal = document.getElementById("place-details-modal");
    const modalContent = document.getElementById("modal-place-details");



    modalContent.innerHTML = `
        <h3>${data.name}</h3>
        <div class="carousel">
            <div class="carousel-images" id="image-carousel"></div>
            <button class="carousel-button prev" onclick="showPreviousImage()">&#10094;</button>
            <button class="carousel-button next" onclick="showNextImage()">&#10095;</button>
        </div>
        <p><strong>Description:</strong> ${data.description}</p>
        <p><strong>Address:</strong> ${data.address}</p>
        <p><strong>Entrance Fee:</strong> ${data.entrance_fee}</p>
        <p><strong>Opening Hours:</strong> ${data.opening_hours}</p>
    `;
    const imageCarousel = document.getElementById("image-carousel");
    imageCarousel.innerHTML = ""; // Clear previous images
    currentImageIndex = 0; // Reset image index

    if (data.image_urls && data.image_urls.length > 0) {
        data.image_urls.forEach((url, index) => {
            const img = document.createElement("img");
            img.src = url;
            img.alt = `Image ${index + 1} of ${data.name}`;
            img.style.display = index === 0 ? 'block' : 'none'; // Show only the first image initially
            imageCarousel.appendChild(img);
        });
    } else {
        // If no images, display a placeholder
        imageCarousel.innerHTML = "<p>No images available.</p>";
    }

    modal.style.display = "block";
}

function showPreviousImage() {
    const images = document.querySelectorAll('#image-carousel img');
    images[currentImageIndex].style.display = 'none';
    currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
    images[currentImageIndex].style.display = 'block';
}

function showNextImage() {
    const images = document.querySelectorAll('#image-carousel img');
    images[currentImageIndex].style.display = 'none';
    currentImageIndex = (currentImageIndex + 1) % images.length;
    images[currentImageIndex].style.display = 'block';
}

function closePlaceDetails() {
    const modal = document.getElementById("place-details-modal");
    modal.style.display = "none";
    document.getElementById("overlay").classList.add("hidden");
}
window.onclick = function(event) {
    const modal = document.getElementById("place-details-modal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
}

      // Open modal when any tourist spot is clicked
      document.querySelectorAll('.tourist-spot').forEach(spot => {
        spot.addEventListener('click', () => {
          document.getElementById("popup-modal").style.display = "block";
        });
      });
  
      // Close modal
      document.querySelector('.close-btn').addEventListener('click', () => {
        document.getElementById("popup-modal").style.display = "none";
      });
  
      // Also close when clicking outside the popup
      window.addEventListener('click', (event) => {
        const modal = document.getElementById("popup-modal");
        if (event.target === modal) {
          modal.style.display = "none";
        }
      });


 // Enable rotation for the container
 const block = document.querySelector(".container");
 let isDragging = false;
 let startX,
   startY,
   currentX = 0,
   currentY = 0;

 document.addEventListener("mousedown", (e) => {
   isDragging = true;
   startX = e.clientX - currentX;
   startY = e.clientY - currentY;
 });

 document.addEventListener("mousemove", (e) => {
   if (!isDragging) return;
   currentX = e.clientX - startX;
   currentY = e.clientY - startY;
   block.style.transform = `rotateX(${currentY}deg) rotateY(${currentX}deg)`;
 });

 document.addEventListener("mouseup", () => {
   isDragging = false;
   snapBack();
 });

 document.addEventListener("touchstart", (e) => {
   isDragging = true;
   startX = e.touches[0].clientX - currentX;
   startY = e.touches[0].clientY - currentY;
 });

 document.addEventListener("touchmove", (e) => {
   if (!isDragging) return;
   currentX = e.touches[0].clientX - startX;
   currentY = e.touches[0].clientY - startY;
   block.style.transform = `rotateX(${currentY}deg) rotateY(${currentX}deg)`;
 });

 document.addEventListener("touchend", () => {
   isDragging = false;
   snapBack();
 });

 function snapBack() {
   block.style.transition = "transform 0.6s ease";
   block.style.transform = "rotateX(0deg) rotateY(0deg)";
   currentX=0;
   currentY=0;
 }     
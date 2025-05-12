
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
    }

    // Update the existing AJAX call to use the modal
    $(document).ready(function () {
        $(".tourist-spot").click(function (e) {
            e.preventDefault();
            let spotName = $(this).data("name");

            $.ajax({
                url: "/get_place_details/",
                type: "GET",
                data: { name: spotName },
                success: function (data) {
                    openPlaceDetails(data);
                }
            });
        });
    });

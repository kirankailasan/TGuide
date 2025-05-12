document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("search-input");
    const searchButton = document.getElementById("search-button");
    const suggestionsContainer = document.createElement("div");
    suggestionsContainer.classList.add("autocomplete-suggestions");
    searchInput.parentNode.appendChild(suggestionsContainer);
    
    let map; // Store map instance
    let marker; // Store marker instance
    let currentImageIndex = 0; // Track current image index in carousel

    // Fetch autocomplete suggestions
    async function fetchSuggestions(query) {
        if (query.length < 2) {
            suggestionsContainer.innerHTML = "";
            return;
        }

        try {
            const response = await fetch(`/search/?query=${query}`);
            const data = await response.json();

            // Show autocomplete suggestions
            suggestionsContainer.innerHTML = "";
            data.suggestions.forEach(item => {
                let suggestion = document.createElement("div");
                suggestion.classList.add("suggestion-item");
                suggestion.textContent = item.name;
                suggestion.addEventListener("click", function () {
                    searchInput.value = item.name;
                    suggestionsContainer.innerHTML = "";
                    performSearch();
                });
                suggestionsContainer.appendChild(suggestion);
            });

            // Show related places if no exact matches
            if (data.related_places.length > 0) {
                let header = document.createElement("div");
                header.classList.add("suggestion-header");
                header.textContent = "Related Places:";
                suggestionsContainer.appendChild(header);

                data.related_places.forEach(item => {
                    let suggestion = document.createElement("div");
                    suggestion.classList.add("suggestion-item");
                    suggestion.textContent = item.name;
                    suggestion.addEventListener("click", function () {
                        searchInput.value = item.name;
                        suggestionsContainer.innerHTML = "";
                        performSearch();
                    });
                    suggestionsContainer.appendChild(suggestion);
                });
            }

        } catch (error) {
            console.error("Error fetching suggestions:", error);
        }
    }

    // Fetch results as user types
    searchInput.addEventListener("input", function () {
        fetchSuggestions(this.value);
    });

    // Trigger search on Enter key
    searchInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            performSearch();
        }
    });

    // Perform search on button click
    searchButton.addEventListener("click", function () {
        performSearch();
    });

    // Perform search and display results
    async function performSearch() {
        let query = searchInput.value.trim();
        if (!query) return;

        try {
            const response = await fetch(`/search/?query=${query}`);
            const data = await response.json();

            if (data.selected_place) {
                displaySearchResults(data.selected_place);
            } else {
                document.getElementById("place-details").innerHTML = "<p>No results found.</p>";
            }

        } catch (error) {
            console.error("Search error:", error);
        }
    }

    // Display search results
    function displaySearchResults(place) {
        document.getElementById("place-name").textContent = place.name;
        document.getElementById("place-description").textContent = place.description || "No description available.";
        document.getElementById("place-address").textContent = place.address || "No address available.";
        document.getElementById("place-opening-hours").textContent = "Opening Hours: " + (place.opening_hours || "Not available");
        document.getElementById("place-entrance-fee").textContent = "Entrance Fee: " + (place.entrance_fee || "Not available");
        
        // Initialize map only once
        if (!map) {
            map = L.map("map").setView([place.latitude, place.longitude], 13);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);
        } else {
            map.setView([place.latitude, place.longitude], 13); // Update map view
        }

        // Remove previous marker if it exists
        if (marker) {
            map.removeLayer(marker);
        }

        // Add new marker
        marker = L.marker([place.latitude, place.longitude]).addTo(map)
            .bindPopup(`<b>${place.name}</b><br>${place.address}`)
            .openPopup();

        // Display images in carousel
        const imageCarousel = document.getElementById("image-carousel");
        imageCarousel.innerHTML = ""; // Clear previous images
        currentImageIndex = 0; // Reset image index

        if (place.image_urls && place.image_urls.length > 0) {
            place.image_urls.forEach((url, index) => {
                const img = document.createElement("img");
                img.src = url;
                img.alt = `Image ${index + 1} of ${place.name}`;
                if (index === 0) {
                    img.classList.add("active");
                }
                imageCarousel.appendChild(img);
            });

            // Add event listeners for carousel buttons
            document.querySelector(".carousel-button.prev").addEventListener("click", showPreviousImage);
            document.querySelector(".carousel-button.next").addEventListener("click", showNextImage);
        } else {
            // If no images, display a placeholder
            imageCarousel.innerHTML = "<p>No images available.</p>";
        }
    }

    // Show previous image in carousel
    function showPreviousImage() {
        const images = document.querySelectorAll("#image-carousel img");
        if (images.length === 0) return;

        images[currentImageIndex].classList.remove("active");
        currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
        images[currentImageIndex].classList.add("active");
    }

    // Show next image in carousel
    function showNextImage() {
        const images = document.querySelectorAll("#image-carousel img");
        if (images.length === 0) return;

        images[currentImageIndex].classList.remove("active");
        currentImageIndex = (currentImageIndex + 1) % images.length;
        images[currentImageIndex].classList.add("active");
    }
});


//image cube
  const faces = [
    document.getElementById('face1'), // front
    document.getElementById('face2'), // right
    document.getElementById('face3'), // back
    document.getElementById('face4'), // left
    document.getElementById('face5'), // top
    document.getElementById('face6')  // bottom
  ];

  function showFace(index) {
    faces.forEach((el, i) => {
      el.classList.toggle('show', i === index);
    });
  }

  function scheduleFaces() {
    const baseDelays = [0, 4166, 8332, 12498, 16664, 20830];
    const offset = 400; // ms before the actual face change
    const delays = baseDelays.map(d => Math.max(d - offset, 10)); // subtract offset but not below 0

    delays.forEach((delay, i) => {
      setTimeout(() => showFace(i), delay);
    });

    setTimeout(scheduleFaces, 25000); // restart after full rotation
  }

  // Start
  showFace(0); // show front initially
  scheduleFaces();
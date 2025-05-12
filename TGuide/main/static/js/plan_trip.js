document.addEventListener("DOMContentLoaded", function () {
  const selectedMultiDiv = document.getElementById("selected-multi-locations");

  // Update the UI when locations change
  function updateSelectedMultiLocationsUI() {
    selectedMultiDiv.innerHTML = "";

    if (selectedMultiLocations.length === 0) {
      selectedMultiDiv.style.display = "none";
      return;
    }

    selectedMultiDiv.style.display = "block";

    selectedMultiLocations.forEach((loc, idx) => {
      const tag = document.createElement("span");
      tag.textContent = loc;
      tag.className = "location-tag";
      tag.style = "display:inline-block;background:#e0e0e0;padding:3px 8px;margin:2px;border-radius:12px;";

      const removeBtn = document.createElement("button");
      removeBtn.textContent = "×";
      removeBtn.type = "button";
      removeBtn.style = "margin-left:4px;background:none;border:none;color:#c00;font-weight:bold;cursor:pointer;";
      removeBtn.onclick = () => {
        selectedMultiLocations.splice(idx, 1);
        updateSelectedMultiLocationsUI();
      };

      tag.appendChild(removeBtn);
      selectedMultiDiv.appendChild(tag);
    });
  }

  // Handle clicks on dynamically added '+' buttons
  document.body.addEventListener("click", function (e) {
    if (e.target.classList.contains("add-spot-btn")) {
      const parent = e.target.closest(".b") || e.target.closest("div");
      const label = parent.querySelector(".b-label") || parent.querySelector("h3");
      if (!label) return;

      const spotName = label.textContent.trim();
      if (!selectedMultiLocations.includes(spotName)) {
        selectedMultiLocations.push(spotName);
        updateSelectedMultiLocationsUI();
      }
    }
  });

  // Pause spot rotation on click
  const cube = document.getElementById('district-imgs');
  cube.addEventListener('click', function () {
    cube.style.animationPlayState = 'paused';
    setTimeout(() => {
      cube.style.animationPlayState = 'running';
    }, 5000);
  });

  // Fetch and render spots by district
  document.getElementById('district-select').addEventListener('change', function () {
    
    const districtName = this.value;
    if (!districtName) return;

    fetch(`/get_spots/${districtName}/`)
      .then(response => response.json())
      .then(spots => {
        const cubeContainer = document.getElementById('district-imgs');
        cubeContainer.innerHTML = '';

        if (spots.length === 0) {
          cubeContainer.innerHTML = '<p>No tourist spots found for this district.</p>';
          return;
        }

        const numFaces = 8;
        const itemsPerFace = 4;
        let imgIndex = 0;

        for (let face = 0; face < numFaces; face++) {
          const span = document.createElement('span');
          span.style.setProperty('--i', face + 1);

          let dboxHtml = `<div class="dbox">`;
          for (let b = 0; b < itemsPerFace; b++) {
            let spot;

            if (imgIndex < spots.length) {
              spot = spots[imgIndex];
            } else {
              const middleStart = Math.floor(spots.length / 4);
              const middleEnd = Math.floor(spots.length * 3 / 4);
              const randomIndex = middleStart + Math.floor(Math.random() * Math.max(1, middleEnd - middleStart));
              spot = spots[randomIndex % spots.length];
            }

            const imgUrl = spot.first_image || 'https://via.placeholder.com/200';
            dboxHtml += `
            
              <div class="b">
                <button class="add-spot-btn">+</button>
                <img src="${imgUrl}" alt="Spot Image">
                <div class="b-label">${spot.name}</div>
              </div>
            `;
            imgIndex++;
          }

          dboxHtml += `</div>`;
          span.innerHTML = dboxHtml;
          cubeContainer.appendChild(span);
        }

        // Update tourist spot list below the cube
        const listContainer = document.getElementById('tourist-spots-container');
        listContainer.innerHTML = '';
        spots.forEach(spot => {
          const div = document.createElement('div');
          div.innerHTML = `
            <h3>${spot.name}</h3>
            <button class="add-spot-btn">+</button>
            <img src="${spot.first_image || 'https://via.placeholder.com/200'}" alt="${spot.name}" width="200">
          `;
          listContainer.appendChild(div);
        });
      })
      .catch(error => {
        console.error('Error fetching spots:', error);
      });
  });
});

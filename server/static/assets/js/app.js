// CREATE AND ADD A STYLE ELEMENT TO CUSTOMIZE PASSWORD VISIBILITY ICONS HOVER EFFECT
var style = document.createElement('style');
style.innerHTML = `
.fa-eye:hover, .fa-copy:hover {
  cursor: pointer;
}
.fa-eye-slash:hover {
  cursor: pointer;
}
`;
document.head.appendChild(style);

// TARGET PASSWORD INPUT AND VISIBILITY ICON FOR TOGGLING VISIBILITY FUNCTIONALITY
const passwordEI = document.querySelector('#password');
const eyeButton = document.querySelector('.fa');
// FLAG TO TRACK PASSWORD VISIBILITY STATE
let isPass = true;
// FUNCTION TO TOGGLE PASSWORD VISIBILITY
function togglePass() {
  if (isPass) {
    // SET INPUT TYPE TO TEXT AND CHANGE ICON TO 'HIDE'
    passwordEI.type = 'text';
    eyeButton.classList.remove('fa-eye');
    eyeButton.classList.add('fa-eye-slash');
    isPass = false;
    eyeButton.title = 'Hide password';
  } else {
    // REVERT INPUT TYPE TO PASSWORD AND CHANGE ICON TO 'SHOW'
    passwordEI.type = 'password';
    eyeButton.classList.remove('fa-eye-slash');
    eyeButton.classList.add('fa-eye');
    isPass = true;
    eyeButton.title = 'Show password';
  }
}

// TARGET CONFIRM PASSWORD INPUT FIELD AND ICON
const confirmPasswordEI = document.querySelector('#confirm_password');
const confirmPassEyeButton = document.querySelector('#confirmPassIcon');
// FLAG TO TRACK CONFIRM PASSWORD VISIBILITY STATE
let isShow = true;
// FUNCTION TO TOGGLE CONFIRM PASSWORD VISIBILITY
function toggleConfirmPass() {
  if (isShow) {
    // SET INPUT TYPE TO TEXT AND CHANGE ICON TO 'HIDE'
    confirmPasswordEI.type = 'text';
    confirmPassEyeButton.classList.remove('fa-eye');
    confirmPassEyeButton.classList.add('fa-eye-slash');
    isShow = false;
    confirmPassEyeButton.title = 'Hide password';
  } else {
    // REVERT INPUT TYPE TO PASSWORD AND CHANGE ICON TO 'SHOW'
    confirmPasswordEI.type = 'password';
    confirmPassEyeButton.classList.remove('fa-eye-slash');
    confirmPassEyeButton.classList.add('fa-eye');
    isShow = true;
    confirmPassEyeButton.title = 'Show password';
  }
}

// ADD EVENT LISTENER TO HANDLE HEADER STYLE CHANGE ON SCROLL
document.addEventListener('DOMContentLoaded', () => {
  const handleScrollHeader = () => {
    const header = document.querySelector('.header');
    // ADD CLASS 'SCROLL-HEADER' WHEN SCROLLING PAST 50PX
    if (window.scrollY >= 50) {
      header.classList.add('scroll-header');
    } else {
      // REMOVE CLASS WHEN SCROLLING ABOVE 50PX
      header.classList.remove('scroll-header');
    }
  };

  // ATTACH SCROLL EVENT LISTENER TO WINDOW OBJECT
  window.addEventListener('scroll', handleScrollHeader);
});

// FUNCTION TO TOGGLE NAV MENU VISIBILITY
function navToggle() {
  const navMenu = document.getElementById('nav-menu');
  navMenu.classList.toggle('show');
}

// FUNCTION TO CLOSE NAV MENU WHEN CLICKING OUTSIDE IT
function handleOutsideClick(event) {
  const navMenu = document.getElementById('nav-menu');
  const toggleButton = document.getElementById('nav-toggle');

  // VERIFY IF CLICKED OUTSIDE BOTH NAV MENU AND TOGGLE BUTTON
  if (!navMenu.contains(event.target) && !toggleButton.contains(event.target)) {
    navMenu.classList.remove('show');
  }
}

// ADD CLICK EVENT LISTENER TO NAV TOGGLE BUTTON
const toggleButton = document.getElementById('nav-toggle');
toggleButton.addEventListener('click', navToggle);

// ADD CLICK EVENT LISTENER TO HANDLE CLICKS OUTSIDE NAV MENU
window.addEventListener('click', handleOutsideClick);

// ADD SCROLL LISTENER TO SHOW SCROLL-UP BUTTON WHEN SCROLLING BEYOND SPECIFIED POINT
document.addEventListener('DOMContentLoaded', () => {
  const handleScroll = () => {
    const scrollUp = document.querySelector('.scrollup');
    if (window.scrollY >= 560) {
      // DISPLAY SCROLL-UP BUTTON WHEN SCROLLING BEYOND 560PX
      scrollUp.classList.add('show-scroll');
    } else {
      // HIDE SCROLL-UP BUTTON WHEN SCROLLING ABOVE 560PX
      scrollUp.classList.remove('show-scroll');
    }
  };

  // ATTACH SCROLL EVENT LISTENER TO WINDOW OBJECT
  window.addEventListener('scroll', handleScroll);

  // REMOVE EVENT LISTENER WHEN PAGE UNLOADS TO AVOID MEMORY LEAK
  window.onbeforeunload = () => {
    window.removeEventListener('scroll', handleScroll);
  };
});

// CLONE CAROUSEL SLIDES TO CREATE A SEAMLESS EFFECT
const companyCarouselTrack = document.querySelector('.company__carousel-track');
const companySlides = document.querySelectorAll('.company__carousel-slide');

companySlides.forEach((companySlide) => {
  // CLONE EACH SLIDE AND APPEND TO THE CAROUSEL TRACK
  const clone = companySlide.cloneNode(true);
  companyCarouselTrack.appendChild(clone);
});

// HERO-SWIPER INITIALIZATION WITH DYNAMIC SLIDES
document.addEventListener('DOMContentLoaded', () => {
  const heroRight = document.querySelector('.hero__right');

  // CREATE SWIPER CONTAINER AND WRAPPER
  const heroRightSwiperContainer = document.createElement('div');
  heroRightSwiperContainer.className = 'swiper hero__swiper-container';
  const heroRightSwiperWrapper = document.createElement('div');
  heroRightSwiperWrapper.className = 'swiper-wrapper hero__swiper-wrapper';

  // APPEND SWIPER WRAPPER TO CONTAINER AND ADD TO DOM
  heroRightSwiperContainer.appendChild(heroRightSwiperWrapper);
  heroRight.appendChild(heroRightSwiperContainer);

  // FETCH HERO SLIDER DATA FROM JSON FILE
  fetch('/hero/api/nfts/')
    .then((response) => {
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }
      return response.json();
    })
    .then((nfts) => {
      nfts.sort(() => Math.random() - 0.5);
      nfts.forEach((nft) => {
        const image = nft.nft_image || '/static/assets/images/default_img.avif';
        const name = nft.nft_name || 'Unnamed NFT';
        const link = '/category';
        const heroRightSlide = document.createElement('a');
        heroRightSlide.className = 'swiper-slide hero__swiper-card';
        heroRightSlide.href = `/category`;
        heroRightSlide.innerHTML = `
          <img src="${image}" alt="Banner Image" />
          <div class="hero__img-content">
            <span class="creator whiteText">
              <!-- Created by <br /> -->
              <p class="yellowText">${name} <i class="bx bxs-badge-check"></i></p>
            </span>
            <a href="${link}">
                <button class="btn">Explore NFT</button>
            </a>
          </div>
        `;
        heroRightSwiperWrapper.appendChild(heroRightSlide);
      });

      // INITIALIZE HERO SWIPER
      new Swiper('.hero__swiper-container', {
        loop: true,
        slidesPerView: 1,
        spaceBetween: 30,
        lazy: { loadPrevNext: true },
        autoplay: { delay: 2000 },
        speed: 1500,
      });
    })
    .catch((error) => {
      console.error('Error loading data:', error);
    });
});

// BSL-SWIPER INITIALIZATION WITH DYNAMIC SLIDES
document.addEventListener('DOMContentLoaded', () => {
  const bslSwiperWrapper = document.querySelector('.bsl__swiper-wrapper');

  // FETCH BSL SLIDER DATA FROM JSON FILE
  fetch('/bsl/api/nfts/')
    .then((response) => response.json())
    .then((nfts) => {
      nfts.sort(() => Math.random() - 0.5);
      // Dynamically populate slides
      nfts.forEach((nft) => {
        const image = nft.nft_image || '/static/assets/images/default_img.avif';
        const name = nft.nft_name || 'Unnamed NFT';
        const category = nft.category || 'Unknown Category';
        const bslSlide = document.createElement('a');
        bslSlide.className = 'bsl__img-card swiper-slide';
        bslSlide.href = '/category';
        bslSlide.innerHTML = `
          <img src="${image}" alt="Image for ${name}" class="bsl__img" />
          <p class="bsl__category-des">${category}</p>
          <h3 class="bsl__name">${name}</h3>
        `;
        bslSwiperWrapper.appendChild(bslSlide);
      });

      // INITIALIZE BSL SWIPER
      new Swiper('.bsl__swiper-container', {
        loop: true, // Enables infinite loop
        navigation: {
          nextEl: '.bsl-swiper-button-next',
          prevEl: '.bsl-swiper-button-prev',
        },
        slidesPerView: 1,
        spaceBetween: 50,
        breakpoints: {
          480: {
            slidesPerView: 1,
          },
          542: {
            slidesPerView: 2,
          },
        },
        lazy: {
          loadPrevNext: true,
        },
        autoplay: {
          delay: 2000, // Autoplay every 3 seconds
        },
        speed: 1500, // Speed of transition in ms
      });
    })
    .catch((error) => console.error('Error fetching data:', error));
});

// TTP-ITEM INITIALIZATION DYNAMICALLY
document.addEventListener('DOMContentLoaded', () => {
  const ttpContent = document.querySelector('.ttp__content');
  ttpContent.innerHTML = '<p>Loading NFTs...</p>';

  fetch('ttp/api/nfts/') // ✅ Fetch from Flask API instead of JSON file
    .then((response) => {
      if (!response.ok) throw new Error('Failed to fetch NFTs');
      return response.json();
    })
    .then((nfts) => {
      ttpContent.innerHTML = '';
      if (nfts.length === 0) {
        ttpContent.innerHTML = '<p>No NFTs available at the moment.</p>';
        return;
      }

      nfts.forEach((nft) => {
        const image = nft.nft_image || '/static/assets/images/default_img.avif';
        const name = nft.nft_name || 'Unnamed NFT';
        const category = nft.category || 'Unknown Category';
        const price = nft.price ? `${nft.price}` : 'N/A';
        const status = nft.status;

        const ttpItem = document.createElement('a');
        ttpItem.className = 'ttp__item';
        ttpItem.href = `nft/buy/nft_${nft.ref_number}`; // ✅ Dynamically inserting NFT reference number

        ttpItem.innerHTML = `
          <img src="${image}" alt="${name}" class="ttp__img" />
          <p class="ttp__category-des">${category}</p>
          <h3 class="ttp__name">${name}</h3>
          <button class="btn flexColCenter">Price: ${price} ETH <small>${status}</small></button>
        `;

        ttpContent.appendChild(ttpItem);
      });
    })
    .catch((error) => {
      console.error('Error fetching NFTs:', error);
      ttpContent.innerHTML = `<p>Error loading NFTs. Please try again later</p>`;
    });
});

// NL-ITEM INITIALIZATION DYNAMICALLY
document.addEventListener('DOMContentLoaded', () => {
  // SELECT THE ELEMENT WHERE DATA WILL BE APPENDED
  const nlContent = document.querySelector('.nl__content');

  // DISPLAY A TEMPORARY LOADING MESSAGE WHILE DATA IS BEING FETCHED
  nlContent.innerHTML = '<p>Loading...</p>';

  // USE THE FETCH API TO RETRIEVE DATA FROM THE SPECIFIED JSON FILE
  fetch('nl/api/nfts/')
    .then((response) => {
      if (!response.ok) throw new Error('Failed to fetch NFTs');
      return response.json();
    })
    .then((nfts) => {
      nlContent.innerHTML = '';
      if (nfts.length === 0) {
        nlContent.innerHTML = '<p>No NFTs available at the moment.</p>';
        return;
      }

      nfts.forEach((nft) => {
        const image = nft.nft_image || '/static/assets/images/default_img.avif';
        const name = nft.nft_name || 'Unnamed NFT';
        const category = nft.category || 'Unknown Category';
        const price = nft.price ? `${nft.price}` : 'N/A';
        const status = nft.status.charAt(0).toUpperCase() + nft.status.slice(1);

        // CREATE A NEW DIV ELEMENT TO REPRESENT AN ITEM
        const nlItem = document.createElement('a');
        nlItem.className = 'nl__item'; // ASSIGN CLASS NAME FOR STYLING
        nlItem.href = `nft/buy/nft_${nft.ref_number}`;

        // POPULATE THE ITEM ELEMENT WITH HTML CONTENT
        nlItem.innerHTML = `
          <img src="${image}" alt="${name}" class="nl__img" aria-label="Image of ${name}" />
          <p class="nl__category-des">${category}</p>
          <h3 class="nl__name">${name}</h3>
          <button class="btn flexColCenter" aria-label="View price and availability for ${name}">
              Price: ${price} ETH
              <small>${status}</small>
          </button>
        `;

        // APPEND THE CREATED ITEM TO THE CONTENT CONTAINER
        nlContent.appendChild(nlItem);
      });
    })
    .catch((error) => {
      // HANDLE FETCH ERRORS (E.G., NETWORK ISSUES OR FILE NOT FOUND)
      console.error('Error fetching data:', error); // LOG ERROR TO THE CONSOLE
      nlContent.innerHTML =
        '<p>Error loading items. Please try again later.</p>'; // DISPLAY AN ERROR MESSAGE IN THE UI
    });
});

// DISCOVER INITIALIZATION DYNAMICALLY
document.addEventListener('DOMContentLoaded', () => {
  const filterList = document.querySelectorAll('#filter-list li'); // SELECT ALL FILTER ITEMS
  const discoverContent = document.querySelector('.discover__content'); // SELECT DISCOVER CONTENT CONTAINER

  // DISPLAY A TEMPORARY LOADING MESSAGE WHILE DATA IS BEING FETCHED
  discoverContent.innerHTML = '<p>Loading...</p>';

  // FUNCTION TO HANDLE FILTERING LOGIC
  const handleFilter = (filter) => {
    const discoverItems = document.querySelectorAll('.discover__item'); // SELECT ALL ITEMS TO FILTER

    // UPDATE ACTIVE CLASS ON SELECTED FILTER ITEM
    filterList.forEach((filterItem) => {
      filterItem.classList.remove('active');
      if (filterItem.getAttribute('data-filter') === filter) {
        filterItem.classList.add('active');
      }
    });

    // LOGIC FOR "ALL" FILTER TO DISPLAY ONLY ONE ITEM PER CATEGORY
    if (filter === 'All') {
      const displayedCategories = new Set(); // TRACK DISPLAYED CATEGORIES

      discoverItems.forEach((item) => {
        const itemCategory = item.getAttribute('data-category');
        if (!displayedCategories.has(itemCategory)) {
          item.style.display = 'block'; // SHOW FIRST ITEM OF EACH CATEGORY
          displayedCategories.add(itemCategory); // ADD CATEGORY TO TRACKED LIST
        } else {
          item.style.display = 'none'; // HIDE OTHER ITEMS IN SAME CATEGORY
        }
      });
    } else {
      // EXISTING LOGIC FOR SPECIFIC CATEGORY FILTER
      discoverItems.forEach((item) => {
        const itemCategory = item.getAttribute('data-category');
        if (itemCategory === filter) {
          item.style.display = 'block'; // SHOW ITEMS MATCHING THE SELECTED CATEGORY
        } else {
          item.style.display = 'none'; // HIDE NON-MATCHING ITEMS
        }
      });
    }
  };

  // ATTACH CLICK EVENT TO EACH FILTER ITEM
  filterList.forEach((filterItem) => {
    filterItem.addEventListener('click', () => {
      const filter = filterItem.getAttribute('data-filter'); // RETRIEVE FILTER VALUE
      handleFilter(filter); // APPLY FILTER
    });
  });

  // USE THE FETCH API TO RETRIEVE DATA FROM THE SPECIFIED JSON FILE
  fetch('/api/nfts/')
    .then((response) => {
      if (!response.ok) throw new Error('Failed to fetch data');
      return response.json();
    })
    .then((nfts) => {
      // ✅ Clear content only once before populating NFTs
      discoverContent.innerHTML = '';

      if (nfts.length === 0) {
        discoverContent.innerHTML = '<p>No items available at the moment.</p>';
        return;
      }

      nfts.forEach((nft) => {
        const image = nft.nft_image || '/static/assets/images/default_img.avif';
        const category = nft.category || 'Unknown Category';
        const name = nft.nft_name || 'Unnamed Nft';
        const price = nft.price || 'N/A';
        const status = nft.status || 'Unavailable';

        const discoverItem = document.createElement('a');
        discoverItem.className = 'discover__item';
        discoverItem.setAttribute('data-category', category);
        discoverItem.href = `nft/buy/nft_${nft.ref_number}`;

        discoverItem.innerHTML = `
        <img src="${image}" alt="${name}" class="discover__img" />
        <p class="discover__category-des">${category}</p>
        <h3 class="discover__name">${name}</h3>
        <button class="btn flexColCenter">Price: ${price} ETH <small>${status}</small></button>
      `;

        discoverContent.appendChild(discoverItem); // ✅ Items are properly appended after clearing
      });

      handleFilter('All'); // ✅ Apply default filter AFTER items are loaded
    })
    .catch((error) => {
      console.error('Error fetching data:', error);
      discoverContent.innerHTML =
        '<p>Error loading items. Please try again later.</p>';
    });
});

// EXP INITIALIZATION DYNAMICALLY
document.addEventListener('DOMContentLoaded', () => {
  const expSwiperWrapper = document.querySelector('.exp__swiper-wrapper');

  // FETCH DATA FROM JSON FILE
  fetch('/exp/api/nfts/')
    .then((response) => response.json())
    .then((nfts) => {
      expSwiperWrapper.innerHTML = '';
      if (nfts.length === 0) {
        expSwiperWrapper.innerHTML = '<p>No NFTs available at the moment.</p>';
        return;
      }

      nfts.forEach((nft) => {
        const image = nft.nft_image || '/static/assets/images/default_img.avif';
        const name = nft.nft_name || 'Unnamed NFT';
        const category = nft.category || 'Unknown Category';
        const expSlide = document.createElement('a');
        expSlide.className = 'exp__swiper-card swiper-slide';
        expSlide.href = `category/${category
          .replace(/\s+/g, '-')
          .toLowerCase()}`;
        expSlide.innerHTML = `
          <img src="${image}" alt="Image for ${name}" class="exp__img" />
          <div class="exp__img-content">
            <h2 class="exp__category-des whiteText">${category}</h2>
          </div>
        `;
        expSwiperWrapper.appendChild(expSlide);
      });

      // INITIALIZE SWIPER
      new Swiper('.exp__swiper-container', {
        loop: true, // Enables infinite loop
        navigation: {
          nextEl: '.exp-swiper-button-next',
          prevEl: '.exp-swiper-button-prev',
        },
        slidesPerView: 1,
        spaceBetween: 40,
        breakpoints: {
          640: {
            slidesPerView: 1,
          },
          750: {
            slidesPerView: 3,
          },
          1500: {
            slidesPerView: 4,
          },
        },
        lazy: {
          loadPrevNext: true,
        },
        autoplay: {
          delay: 2000, // Autoplay every 2 seconds
        },
        speed: 1500, // Speed of transition in ms
      });
    })
    .catch((error) => console.error('Error fetching data:', error));
});

// CATEGORY PAGE INITIALIZATION DYNAMICALLY
document.addEventListener('DOMContentLoaded', () => {
  const categoryContent = document.querySelector('.category__content');
  // DISPLAY A TEMPORARY LOADING MESSAGE WHILE DATA IS BEING FETCHED
  categoryContent.innerHTML = '<p>Loading...</p>';

  // FETCH DATA FROM JSON FILE
  fetch('/exp/api/nfts/')
    .then((response) => response.json())
    .then((nfts) => {
      categoryContent.innerHTML = '';
      if (nfts.length === 0) {
        categoryContent.innerHTML = '<p>No NFTs available at the moment.</p>';
        return;
      }

      nfts.forEach((nft) => {
        const image = nft.nft_image || '/static/assets/images/default_img.avif';
        const name = nft.nft_name || 'Unnamed NFT';
        const category = nft.category || 'Unknown Category';
        const categoryItem = document.createElement('a');
        categoryItem.className = 'category__item';
        categoryItem.href = `category/${category
          .replace(/\s+/g, '-')
          .toLowerCase()}`;
        categoryItem.innerHTML = `
          <img src="${image}" alt="Image for ${name}" class="category__img" />
          <div class="category__img-content">
            <h2 class="category__img-des whiteText">${category}</h2>
          </div>
        `;
        categoryContent.appendChild(categoryItem);
      });
    })
    .catch((error) => console.error('Error fetching data:', error));
});

// ART-ITEM INITIALIZATION DYNAMICALLY
document.addEventListener('DOMContentLoaded', () => {
  const artProfileImg = document.querySelector('.art__profile-img');
  const artContent = document.querySelector('.art__content');
  artContent.innerHTML = '<p>Loading...</p>';

  // ✅ Dynamically derive the category from the `id` of the selected element
  const targetCategory = artContent.id.toLowerCase();

  // ✅ Fetch NFTs based on the category
  fetch(`/api/nfts/${targetCategory}`)
    .then((response) => {
      if (!response.ok) throw new Error('Failed to fetch NFTs');
      return response.json();
    })
    .then((nfts) => {
      artContent.innerHTML = '';
      if (!nfts || nfts.error) {
        artContent.innerHTML = `<p>${
          nfts.error || 'No NFTs available at the moment.'
        }</p>`;
        return;
      }

      // ✅ Set `.art__profile-img` to the image of the 6th NFT (if available)
      if (nfts.length >= 4) {
        artProfileImg.src =
          nfts[3].nft_image || '/static/assets/images/default_img.avif';
      }

      // ✅ Display NFTs in the `.art__content` section
      nfts.forEach((nft) => {
        const image = nft.nft_image || '/static/assets/images/default_img.avif';
        const name = nft.nft_name || 'Unnamed NFT';
        const price = nft.price ? `${nft.price} ETH` : 'N/A';
        const status = nft.status.charAt(0).toUpperCase() + nft.status.slice(1);

        const artItem = document.createElement('a');
        artItem.className = 'art__item';
        artItem.href = `nft/buy/nft_${nft.ref_number}`;

        artItem.innerHTML = `
          <img src="${image}" alt="${name}" class="art__img" aria-label="Image of ${name}" />
          <h3 class="art__name">${name}</h3>
          <button class="btn flexColCenter" aria-label="View price and availability for ${name}">
              Price: ${price}
              <small>${status}</small>
          </button>
        `;

        artContent.appendChild(artItem);
      });
    })
    .catch((error) => {
      console.error('Error fetching NFTs:', error);
      artContent.innerHTML =
        '<p>Error loading NFTs. Please try again later.</p>';
    });
});

// EXPLORE-ITEM INITIALIZATION DYNAMICALLY
document.addEventListener('DOMContentLoaded', () => {
  // SELECT THE ELEMENT WHERE DATA WILL BE APPENDED
  const exploreContent = document.querySelector('.explore__content');

  // DISPLAY A TEMPORARY LOADING MESSAGE WHILE DATA IS BEING FETCHED
  exploreContent.innerHTML = '<p>Loading...</p>';

  // USE THE FETCH API TO RETRIEVE DATA FROM THE SPECIFIED JSON FILE
  fetch('/explore/api/nfts/')
    .then((response) => {
      if (!response.ok) throw new Error('Failed to fetch NFTs');
      return response.json();
    })
    .then((nfts) => {
      exploreContent.innerHTML = '';
      if (nfts.length === 0) {
        exploreContent.innerHTML = '<p>No NFTs available at the moment.</p>';
        return;
      }

      // ✅ Shuffle the NFTs randomly before displaying them
      nfts.sort(() => Math.random() - 0.5);

      nfts.forEach((nft) => {
        const image = nft.nft_image || '/static/assets/images/default_img.avif';
        const name = nft.nft_name || 'Unnamed NFT';
        const category = nft.category || 'Unknown Category';
        const price = nft.price ? `${nft.price} ETH` : 'N/A';
        const status = nft.status.charAt(0).toUpperCase() + nft.status.slice(1);

        // CREATE A NEW DIV ELEMENT TO REPRESENT AN ITEM
        const exploreItem = document.createElement('a');
        exploreItem.className = 'explore__item'; // ASSIGN CLASS NAME FOR STYLING
        exploreItem.href = `nft/buy/nft_${nft.ref_number}`;

        // POPULATE THE ITEM ELEMENT WITH HTML CONTENT
        exploreItem.innerHTML = `
          <a href="${image}">
            <img src="${image}" alt="${name}" class="explore__img" aria-label="Image of ${name}" style="background-image: url('${image}');"/>
          </a>
          <p class="explore__category-des">${category}</p>
          <h3 class="explore__name">${name} <i class="bx bxs-badge-check"></i></h3>
          <button class="btn flexColCenter" aria-label="View price and availability for ${name}">
              Price: ${price}
              <small>${status}</small>
          </button>
        `;

        // APPEND THE CREATED ITEM TO THE CONTENT CONTAINER
        exploreContent.appendChild(exploreItem);
      });
    })
    .catch((error) => {
      // HANDLE FETCH ERRORS (E.G., NETWORK ISSUES OR FILE NOT FOUND)
      console.error('Error fetching data:', error); // LOG ERROR TO THE CONSOLE
      exploreContent.innerHTML =
        '<p>Error loading items. Please try again later.</p>'; // DISPLAY AN ERROR MESSAGE IN THE UI
    });
});

// ALERTS
document.addEventListener('DOMContentLoaded', () => {
  const alerts = document.querySelectorAll('.alert');

  // Automatically remove alerts after 5 seconds
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.classList.add('fade'); // Add fade-out animation
      setTimeout(() => {
        alert.classList.add('d-none'); // Hide after fade completes
      }, 500); // Duration of fade transition
    }, 10000); // 10000ms = 10 seconds
  });

  // Close alerts when the close button is clicked
  const closeButtons = document.querySelectorAll('.btn-close');
  closeButtons.forEach((button) => {
    button.addEventListener('click', (event) => {
      const alert = event.target.closest('.alert');
      alert.classList.add('fade'); // Add fade-out animation
      setTimeout(() => {
        alert.remove(); // Remove the alert element from the DOM
      }, 500); // Duration of fade transition
    });
  });
});

// COPY TO CLIPBOARD
const copyButton = document.querySelector('.fa-copy');
copyButton.title = 'Copy to clipboaard';
function copyToClipboard(elementId) {
  // Get the element by ID
  const targetElement = document.getElementById(elementId);

  if (targetElement) {
    let textToCopy;

    // Check if the element is an input or textarea
    if (
      targetElement.tagName === 'INPUT' ||
      targetElement.tagName === 'TEXTAREA'
    ) {
      textToCopy = targetElement.value; // Get the value for input/textarea fields
    } else {
      textToCopy = targetElement.innerText || targetElement.textContent; // Get the text for non-input elements
    }

    try {
      // Use navigator.clipboard API to copy the text
      navigator.clipboard
        .writeText(textToCopy)
        .then(() => {
          // Show success message
          alert('Text copied to clipboard!');
        })
        .catch(() => {
          alert('Failed to copy. Please try again.');
        });
    } catch (error) {
      console.error('Copy to clipboard failed:', error);
      alert('Copy function is not supported in this browser.');
    }
  } else {
    console.error(`Element with ID '${elementId}' not found.`);
  }
}

// ACCORDION
function toggleAccordion(buttonElement) {
  const accordionItem = buttonElement.parentElement;
  const isExpanded = accordionItem.classList.contains('expanded');

  if (isExpanded) {
    accordionItem.classList.remove('expanded'); // Collapse only the clicked item
  } else {
    accordionItem.classList.add('expanded'); // Expand the clicked item
  }
}

// Ensure all items are expanded by default when the page loads
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.accordion__item').forEach((item) => {
    item.classList.add('expanded');
  });
});

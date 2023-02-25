function goToIndex() {
    window.location.href = "../index.html";
  }
  
  window.addEventListener('load', initMap);


  var latitude = 0, longitude = 0;
  var radius = 5000;
  var locationError = false;
  const errorMessage = "Unable to retrieve your location. Please try again later.";
  
  //requesting permission to access location
  if (navigator.permissions) {
      navigator.permissions.query({ name: 'geolocation' }).then(permission => {
          if (permission.state === 'granted') {
              // permission granted, call getCurrentPosition()
              navigator.geolocation.getCurrentPosition(successCallback, errorCallback);
          } else if (permission.state === 'prompt') {
              //permission not granted, prompt the user to allow location access
              alert("Please allow location access.");
          } else {
              // permission denied
              console.log("User denied the request for location access.");
          }
      });
  } else {
      // navigator.permissions not supported, call getCurrentPosition()
  }
  
  //using user location data
  navigator.geolocation.getCurrentPosition(successCallback, errorCallback);
  
  function successCallback(position) {
      latitude = position.coords.latitude;
      longitude = position.coords.longitude;
  
      // use the latitude and longitude data
      console.log("Latitude: " + latitude + ", Longitude: " + longitude);
      var x = document.getElementById("demo");
      x.innerHTML = "Latitude: " + latitude + " Longitude: " + longitude;
      initMap();
  }
  
  //handle errors
  function errorCallback(error) {
      locationError = true;
      console.error("Error getting location data: ${error.message}");
      //code to display error message to user on web page
      alert(errorMessage);
  }
  
  //init map function
  function initMap() {
      // Create a new map instance
      var center = new google.maps.LatLng(latitude, longitude);
  
      var map = new google.maps.Map(document.getElementById('map'), {
          center: center,
          zoom: 10
      });
  
      //marker for current location
      var customIcon = {
          url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png', // URL of the custom icon image
          size: new google.maps.Size(32, 32), // Size of the custom icon image
          origin: new google.maps.Point(0, 0), // Position of the custom icon image relative to the top-left corner of the icon image
          anchor: new google.maps.Point(16, 32) // Position of the anchor point on the marker image (where the marker's position is located relative to the icon)
      };
  
      var marker = new google.maps.Marker({
          position: { lat: latitude, lng: longitude },
          icon: customIcon,
          map: map,
          title: 'Current Location'
      });
  
      // Define the info window
      var contentString = '<div id="content">' +
          '<h2 id="firstHeading" class="firstHeading">' + marker.title + '</h2>' +
          '<div id="bodyContent">' +
          '<span>This is your current location.</span>' +
          '</div>' +
          '</div>';
  
      var infowindow = new google.maps.InfoWindow({
          content: contentString
      });
  
  
      // Add event listener to show info window on mouseover
      marker.addListener('mouseover', function () {
          infowindow.open(map, marker);
      });
  
      // Add event listener to hide info window on mouseout
      marker.addListener('mouseout', function () {
          infowindow.close();
      });
  
  
      //===========SEARCH==============
  
      // Create a new Places Service instance
      var service = new google.maps.places.PlacesService(map);
  
      // Define the search query parameters
      var request = {
          location: center,
          radius: radius, // Search within 5 km radius
          query: 'skin dermatologists'
      };
  
      // Send the search request
      service.textSearch(request, callback);
  
      // Define the callback function
      function callback(results, status) {
          if (status == google.maps.places.PlacesServiceStatus.OK) {
              // Loop through the results and create a marker for each one
              for (var i = 0; i < results.length; i++) {
                  createMarker(results[i], results, i);
  
              }
          }
      }
  
      // Create a marker for a place
      function createMarker(place, results, i) {
          //console.log(results);
          var marker = new google.maps.Marker({
              map: map,
              position: place.geometry.location,
              title: place.name,
  
          });
  
          // Create a new info window for each place
          var infowindow = new google.maps.InfoWindow({
              content: '<div style="color: black;"><h3>' + results[i].name + '</h3><p>' + results[i].formatted_address + '</p></div>'
          });
  
          // Add event listeners to show and hide info window
          marker.addListener('mouseover', function () {
              infowindow.open(map, this);
          });
          marker.addListener('mouseout', function () {
              infowindow.close();
          });
  
      }
  
  }
  
  //function to change the radius of the search and then call the initMap function
  function changeRadius() {
      //check what the input of units is
      var units = document.getElementById("units").value;
      var ratio = 1;
      if (units == "miles") {
          ratio = 621.371;
      } else if (units == "kilometers") {
          ratio = 1000;
      }
      var numTest = parseInt(document.getElementById("radius").value);
      if (Number.isInteger(numTest)) {
          radius = document.getElementById("radius").value * ratio;
          initMap();
      } else {
          alert("Input is not an integer");
      }
  
  }
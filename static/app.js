/**
 * Created by buwan on 7/6/2017.
 */
var app = angular.module('hash-tag-investor', ['ngRoute', 'ngSessionStorage', 'ngMap']);

/* particlesJS.load(@dom-id, @path-json, @callback (optional)); */
particlesJS.load('particles-js', 'static/assets/particles.json', function () {
    console.log('callback - particles.js config loaded');
});

// const SERVER_URL = "http://127.0.0.1:6699/api";
const SERVER_URL = "http://hashtag.bmaxtech.org/api";

const icons = {
    tweet: "static/assets/images/pin_1.png",
    re_tweet: "static/assets/images/pin_2.png",
    comment: "static/assets/images/pin_3.png",
    positive: "static/assets/images/pin_4.png",
    negative: "static/assets/images/pin_5.png",
    neutral: "static/assets/images/pin_6.png"
};

/**
 * Map Service
 */
app.service('Map', function ($q) {
    var markers = [];

    function clearMarkers() {
        for (var i = 0; i < markers.length; i++) {
            markers[i].setMap(null);
        }
        markers = [];
    }

    this.init = function (id) {
        clearMarkers();
        var options = {
            center: new google.maps.LatLng(0, 0),
            zoom: 2,
            minZoom: 2,
            disableDefaultUI: true
        };
        return new google.maps.Map(
            document.getElementById(id), options
        );
    };

    this.addMarker = function (type, location, map) {
        markers.push(new google.maps.Marker({
            map: map,
            icon: icons[type],
            position: new google.maps.LatLng(location.lat, location.lng),
            animation: google.maps.Animation.DROP
        }));
    }
});
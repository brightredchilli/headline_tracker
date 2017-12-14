const $ = require('jquery');

$(() => {
  $(".cropped-image")
    .mouseenter(e => {
      const caption = e.currentTarget.querySelector(".cropped-image-caption")
      $(caption).fadeTo(400, 100)
    })
    .mouseleave(e => {
      const caption = e.currentTarget.querySelector(".cropped-image-caption")
      $(caption).fadeTo(400, 0)
    })
});




$(".menu-button").on("click", () => {
  $("nav").toggleClass("show");
  $(".fa-bars").toggleClass("hide");
  $(".fa-xmark").toggleClass("show-icon");
});

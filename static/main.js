$(document).ready(function () {
  $("#loader").hide("fast");

  $("#sub-btn").click(function (e) {
      e.preventDefault()

    if (!$("#twhandle").val()) {
      console.log("bruh");
      $("#twhandle").focus();

    } else {
      $("#form").submit();
      $("#plots").hide("slow");
      $("#loader").show("slow");

      //loading text slideshow
      setInterval(function () {
        $(".ltcontainer :first-child")
          .fadeOut(3000)
          .next(".lt")
          .fadeIn(3000)
          .end()
          .appendTo(".ltcontainer");
      }, 6000);
    }
  });
});

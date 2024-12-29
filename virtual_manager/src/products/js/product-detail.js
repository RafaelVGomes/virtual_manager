$(document).ready(function () {
  // Event triggered when the has_recipe field changes
  $('[name="has_recipe"]').change(function () {
    const hasRecipeValue = $(this).val();
    const action = $(this).data('action').toLowerCase(); // Get action type (e.g., 'update')

    if (action === 'update' && hasRecipeValue === '0') {
      // Display the modal
      $('#has-recipe-modal').modal({
        backdrop: 'static', // Prevent closing by clicking outside
        keyboard: false,   // Prevent closing with the Esc key
      }).modal('show');
    }
  });

  // "Yes" button in the modal
  $('#has-recipe-modal .btn-danger').click(function () {
    // Confirm the change to unchecked
    $('#has_recipe0').prop('checked', true);
    $('#has-recipe-modal').modal('hide');
  });

  // "No" button in the modal
  $('#has-recipe-modal .btn-primary').click(function () {
    // Revert the change to checked
    $('#has_recipe1').prop('checked', true);
    $('#has-recipe-modal').modal('hide');
  });
})


  //   if ($('#form').html()) {
  //     const form = JSON.parse($('#form').html())
  //     Object.entries(form).forEach(([key, value]) => {
  //       key == "has_recipe" ? $(`#has_recipe${value}`).prop('checked', true) : $(`#${key}`).val(value)
  //     })
  //   }
  
  //   if ($(`#has_recipe1`).attr('checked')) {
  //     $('#recipeContainer').show()
  //   } else {
  //     $('#recipeContainer').hide()
  //   }
    
  //   $('[name="has_recipe"]').change(function () {
  //     if ($(this).val() == 1) {
  //       $('#recipeContainer').show()
  //     } else {
  //       $('#recipeContainer').hide()
  //     }
  //   })
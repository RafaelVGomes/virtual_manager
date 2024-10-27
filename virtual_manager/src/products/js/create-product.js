$(document).ready(function () {
  if ($('#form').html()) {
    const form = JSON.parse($('#form').html())
    Object.entries(form).forEach(([key, value]) => {
      key == "has_recipe" ? $(`#has_recipe${value}`).prop('checked', true) : $(`#${key}`).val(value)
    })
  }

  if ($(`#has_recipe1`).attr('checked')) {
    $('#recipeContainer').show()
  } else {
    $('#recipeContainer').hide()
  }
  
  $('[name="has_recipe"]').change(function () {
    if ($(this).val() == 1) {
      $('#recipeContainer').show()
    } else {
      $('#recipeContainer').hide()
    }
  })
})
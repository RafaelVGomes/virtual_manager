$(document).ready(function () {
  recipes_json_handler()
  $("#itemsColumn").children().length == 0 ? create_recipe_form() : null
  $('#addItemBtn').on('click', () => { create_recipe_form() })
  $("#delItemBtn").on('click', () => { delete_recipe_form() })
})


function disable_del_btn() {
  if ($("#itemsColumn").children().length > 1) {
    $('#delItemBtn').prop('disabled', false)
  } else {
    $('#delItemBtn').prop('disabled', true)
  }
}

function create_recipe_form(recipe_id=null) {
  let index = Number($("#recipesIndex").val())
  !recipe_id ? recipe_id = index + 1 : index = recipe_id
  // let totalForms = Number($("#inlineFormsTotal").val())
  const form = $("#inlineRecipe0").clone(true)

  form.prop('id', `inlineRecipe${recipe_id}`)
  
  form.find('#recipeFormId0').prop({
    'id': `recipeFormId${recipe_id}`,
    'name': `recipe${recipe_id}`,
    'value': recipe_id,
  })

  form.find("#delRecipe0").prop({
    'name': `recipe${recipe_id}`,
    'id': `delRecipe${recipe_id}`,
    'value': `#inlineRecipe${recipe_id}`,
    'checked': false
  })

  form.find("label[for='delRecipe0']").prop('for', `delRecipe${recipe_id}`)

  form.find(`select`).prop({'name': `recipe${recipe_id}`, 'id': `itemRecipe${recipe_id}`}).children().each(function() {
    $(this).val() ? $(this).prop('selected', false) : $(this).prop('selected', true)
  })

  form.find("#itemAmount0").prop({
    'name': `recipe${recipe_id}`,
    'id': `itemAmount${recipe_id}`,
    'value': 0
  })

  $("#itemsColumn").append(form)
  index++
  $("#recipesIndex").val(index)
  // totalForms++
  // $("#inlineFormsTotal").val(totalForms)

  disable_del_btn()
}


export function delete_recipe_form() {
  // let totalForms = Number($("#inlineFormsTotal").val())
  $("#itemsColumn").find("input[type=checkbox]:checked").each(function () {
    $($(this).val()).remove()
    // $("#inlineFormsTotal").val(totalForms - 1)
  })

  disable_del_btn()
}

function recipes_json_handler(debug=false) {
  if ($('#recipesData').html()) {
    const recipesData = JSON.parse($('#recipesData').html())
    
    Object.entries(recipesData).forEach(([key, value]) => {
      if (key == 'recipes') {
        Object.keys(recipesData[key]).forEach(recipe => {
          // creates forms
          Object.entries(recipesData[key][recipe]).forEach(([element_id, value]) => {
            element_id.includes('recipeId') ? create_recipe_form(value) : null,
            debug ? log(`${element_id}: ${value}`): null
          })
          // populates forms
          Object.entries(recipesData[key][recipe]).forEach(([element_id, value]) => {
            $(`#${element_id}`).val(value)
          })
        })
      } else {
        // populates anything else
        $(`#${key}`).val(value)
      }
    })
  }
}


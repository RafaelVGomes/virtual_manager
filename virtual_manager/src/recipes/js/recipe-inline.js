import { toast } from "../../../static/components/toast.js"

$(document).ready(function () {
  $('#addJsFormBtn').on('click', () => { create_js_form() })
  $('#delJsFormBtn').on('click', (e) => { delete_js_form(e.currentTarget) })
  $('#delDbFormBtn').on('click', (e) => { delete_db_form(e.currentTarget) })
  $('#jsModal').on('show.bs.modal', (e) => { update_js_modal(e.relatedTarget) })
  $('#dbModal').on('show.bs.modal', (e) => { update_db_modal(e.relatedTarget) })
  check_forms()
})

function create_js_form() {
  let index = Number($('#recipesIndex').val())
  const form = $('#inlineRecipe0').clone(true)
  
  form.attr('id', `inlineRecipe${index}`)
  
  form.find('#recipeId0').attr({
    'id': `recipeId${index}`,
    'name': `recipeId${index}`,
    'value': 0,
  })

  form.find('#modalBtn0').attr({
    'id': `modalBtn${index}`,
    'form-id': `#inlineRecipe${index}`,
    'select-id': `#itemRecipe${index}`
  })

  form.find('#itemRecipe0').attr({
    'id': `itemRecipe${index}`,
    'name': `itemRecipe${index}`
  })

  form.find('#amountRecipe0').attr({
    'id': `amountRecipe${index}`,
    'name': `amountRecipe${index}`
  })
  
  $('#inline-forms').append(`<!-- JS form ${index} -->`).append(form)
  index++
  $('#recipesIndex').val(index)
  check_forms()
}

function update_js_modal(click_btn) {
  const btn = $(click_btn)
  const formId = btn.attr('form-id')
  const form = $(formId)
  const selectId = btn.attr('select-id')
  const selected = form.find(`${selectId} :selected`).val()
  const selectedId = Number(selected.split(',')[0])
  const selectedItem = _.startCase(selected.split(',')[1])
  const modal = $('#jsModal')
  const delFormBtn = modal.find('#delJsFormBtn')
  const modalBodyText = modal.find('#js-modal-body-text')
  
  delFormBtn.attr({'form-id': formId})
  
  $(modalBodyText).text('Are you sure you want to delete this form?')
}

function delete_js_form(click_btn) {
  const form = $($(click_btn).attr('form-id'))
  $(form).remove()
  check_forms()
}

function update_db_modal(click_btn) {
  const btn = $(click_btn)
  const url = btn.attr('endpoint-url')
  const formId = btn.attr('form-id')
  const form = $(formId)
  console.log('form:', form)
  const dbFormItemName = _.startCase(form.find(`#itemRecipeName${formId.replace('#inlineRecipe', '')}`).val())
  console.log('dbFormItemName:', dbFormItemName)
  const selectId = btn.attr('select-id')
  const selected = form.find(`${selectId} :selected`).val()
  const selectedId = Number(selected.split(',')[0])
  const selectedItem = _.startCase(selected.split(',')[1])
  const modal = $('#dbModal')
  const delModalBtn = modal.find('#delDbFormBtn')
  const modalBodyText = modal.find('#db-modal-body-text')
  
  delModalBtn.attr({'data-url': url})
  delModalBtn.attr({'form-id': formId})
  
  $(modalBodyText).html(`Are you sure you want to remove "<strong>${dbFormItemName}</strong>" from this recipe?`)
}

function delete_db_form(click_btn) {
  const btn = $(click_btn)
  const url = $(btn).attr('data-url')
  const formId = btn.attr('form-id')
  const form = $(formId)
  const recipeId = Number(form.find(`#idRecipe${formId}`).val())
  
  if (recipeId !== 0) {
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
    }).then((response) => {
      if (response.ok) {
        toast('Recipe item removed.', 'success')
        delete_js_form(btn)
      } else {
        toast('Item not removed.')
      }
    }).catch((error) => {
      toast('Error while connecting to the server.')
      console.log(error)
    })
  } else {
    delete_js_form(btn)
  }
}

function check_forms() {
  const saveBtn = $('#recipe-save-btn')
  const forms = $('#inline-forms')
  const text = $('<div class="row align-items-center justify-content-center my-3" id="inline-forms-text">Add an item form.</div>')
  if (forms.children().length === 0 && !forms.find('#inline-forms-text').length) {
    forms.append(text)
    saveBtn.attr('disabled', true)
  } else {
    forms.find('#inline-forms-text').remove()
    saveBtn.attr('disabled', false)
  }
}
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
  
  form.find('#IdRecipe0').attr({
    'id': `IdRecipe${index}`,
    'name': `recipe${index}`,
    'value': 0,
  })

  form.find('#modalBtn0').attr({
    'id': `modalBtn${index}`,
    'form-id': `#inlineRecipe${index}`,
    'select-id': `#itemRecipe${index}`
  })

  form.find('#itemRecipe0').attr({
    'id': `itemRecipe${index}`,
    'name': `recipe${index}`
  })

  form.find('#amountRecipe0').attr({
    'id': `amountRecipe${index}`,
    'name': `recipe${index}`
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
  const selectedItem = form.find(`${selectId} :selected`).text()
  const modal = $('#jsModal')
  const delFormBtn = modal.find('#delJsFormBtn')
  const modalBodyText = modal.find('#js-modal-body-text')
  
  delFormBtn.attr({'form-id': formId})
  
  if (selectedItem === '-----------') {
    $(modalBodyText).text('Are you sure you want to delete this form?')
  } else {
    $(modalBodyText).text(`Are you sure you want to delete "${selectedItem}"?`)
  }
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
  const selectId = btn.attr('select-id')
  const selectedItem = form.find(`${selectId} :selected`).text()
  const modal = $('#dbModal')
  const delModalBtn = modal.find('#delDbFormBtn')
  const modalBodyText = modal.find('#db-modal-body-text')
  
  delModalBtn.attr({'data-url': url})
  delModalBtn.attr({'form-id': formId})
  
  if (selectedItem === '-----------') {
    $(modalBodyText).text('Are you sure you want to delete this form?')
  } else {
    $(modalBodyText).text(`Are you sure you want to delete "${selectedItem}"?`)
  }
}

function delete_db_form(click_btn) {
  const btn = $(click_btn)
  const url = $(btn).attr('data-url')
  
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
  }).then((response) => {
    if (response.ok) {
      toast('Recipe item deleted.', 'success')
      delete_js_form(btn)
    } else {
      toast('Item not delete.')
    }
  }).catch((error) => {
    toast('Error while connecting to the server.')
    console.log(error)
  })
}

function check_forms() {
  const forms = $('#inline-forms')
  const text = $('<div class="row align-items-center justify-content-center my-3" id="inline-forms-text">Add an item form.</div>')
  if (forms.children().length === 0 && !forms.find('#inline-forms-text').length) {
    forms.append(text)
  } else {
    forms.find('#inline-forms-text').remove()
  }
}
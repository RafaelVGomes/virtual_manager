$(document).ready(function () {
  adjustInputWidth();
  $(".dynamic-width").on("input", (e) => { adjustInputWidth, checkAccordionData })
  $('.accordion-item').each(function () { checkAccordionData.call(this) })
  $('.accordion-item').on('click', () => { checkAccordionData })
  $(".increment").on('click', (e) => { increment(e.currentTarget) });
  $(".decrement").on('click', (e) => { decrement(e.currentTarget) });
})

// global control
const items = JSON.parse($('#recipes-accordion').attr('data-items'))
let itemsTemp = JSON.parse($('#recipes-accordion').attr('data-items'))
const itemsCtrl = {}

// checks accordion data and handles text colors and buttons states
function checkAccordionData() {
  const prod_id = $(this).data("product-id")
  const input = $(`#${prod_id}-input`)
  const inputValue = parseInt(input.val()) || 0;

  const itemsCheck = {}
  $(`#${prod_id}-items`).find('li').each(function () {
    const elementId = $(this).attr('id')
    const itemId = $(this).data('id')
    const alert = itemsTemp[itemId].alert
    const demandEl = $(`#${elementId}-demand`)
    const demand = parseInt(demandEl.text())
    const demanded = inputValue * demand
    const totalEl = $(`#${elementId}-total`)
    let total = undefined
    
    // Reverts to original state if inputValue is 0
    if (inputValue > 0) {
      total = itemsTemp[itemId].total - demanded
    } else {
      total = items[itemId].total + demanded
    }
    
    itemsTemp[itemId].total = total
    // itemsCtrl[prod_id] = total

    totalEl.text(total)
    
    if (demanded < total) {
      itemsCheck[elementId] = true;
      if (total <= alert) {
        totalEl.css({'color': '#FFB300'})
      } else {
        totalEl.css({'color': 'green'})
      }
    } else {
      itemsCheck[elementId] = false;
      totalEl.css({'color': 'red'})
    }
  })

  const allItemsValid = Object.values(itemsCheck).every((value) => value);
  $(`#${prod_id}-increment`).prop('disabled', !allItemsValid)
  $(`#${prod_id}-decrement`).prop('disabled', !inputValue > 0)
}

// increments a given number
function increment(click_btn) {
  const btn = $(click_btn)
  const prod_id = btn.data("product-id")
  const accordion = $(`.accordion-item[data-product-id="${prod_id}"]`)
  const input = $(`#${prod_id}-input`)
  const inputValue = parseInt(input.val()) || 0;
  
  input.val(inputValue + 1);
  adjustInputWidth();
  checkAccordionData.call(accordion)
}

// decrements a given number
function decrement(click_btn) {
  const btn = $(click_btn)
  const prod_id = btn.data("product-id")
  const accordion = $(`.accordion-item[data-product-id="${prod_id}"]`)
  const input = $(`#${prod_id}-input`)
  const inputValue = parseInt(input.val()) || 0;
  
  input.val(inputValue - 1);
  adjustInputWidth();
  checkAccordionData.call(accordion)
}

// number input size adjustment
function adjustInputWidth() {
  const inputs = $(".dynamic-width");

  inputs.each(function () {
    const input = $(this)
    const value = input.val() || 0;
  
    // temporary element to measure rendered input
    const tempSpan = $("<span>")
      .text(value)
      .css({
        "font-size": input.css("font-size"),
        "font-family": input.css("font-family"),
        "font-weight": input.css("font-weight"),
        "letter-spacing": input.css("letter-spacing"),
        "visibility": "hidden",
        "position": "absolute",
        "white-space": "nowrap",
      });
  
    // Appends temporary span to the body, does measuring and removes it
    $("body").append(tempSpan);
    const textWidth = tempSpan.width();
    tempSpan.remove();
  
    const padding = 27; // extra padding
    input.css("width", `${textWidth + padding}px`);
  });
}

// function produce(amount) {
//   const amount = Number(amount)
// }
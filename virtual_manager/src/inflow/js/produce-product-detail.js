$(document).ready(function () {
  // changes items amounts for user's visual awareness
  $('#amount').on('change', function checkItemsData() {
    const amountEl = $(this)
    
    const itemsCheck = {}
    $('#list').find('li').each(function () {
      const itemId = $(this).data('item-id')
      const alert = $(this).data('alert')
      const max = $(this).data('max')
      const nameEl = $(`#${itemId}-name`)
      const demandEl = $(`#${itemId}-demand`)
      const demand = parseInt(demandEl.text())
      const totalEl = $(`#${itemId}-total`)
      
      if (amountEl.val() > max) {
        amountEl.val(max)
      }
      
      const amountValue = amountEl.val();
      const demanded = amountValue * demand
      let total = undefined
      if (amountValue > 0  && amountValue <= max) {
        total = parseInt($(this).data('total')) - demanded
        $(`.${itemId}`).val(total)
      } else {
        total = $(this).data('total')
        $(`.${itemId}`).val(total)
      }

      totalEl.text(total)
      
      if (demanded < total) {
        itemsCheck[itemId] = true;
        if (total <= alert) {
          totalEl.css({'color': '#FFB300'})
        } else {
          totalEl.css({'color': 'green'})
        }
      } else {
        itemsCheck[itemId] = false;
        totalEl.css({'color': 'red'})
        nameEl.css({'color': 'red'})
      }
    })
  
    // const allItemsValid = Object.values(itemsCheck).every((value) => value);
    // $('#save').prop('disabled', !amountEl.val() > 0)
  })
})

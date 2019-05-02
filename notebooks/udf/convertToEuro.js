function convertToEuro(currency_in_usd_text) {
    var currency_in_usd_number = Number(currency_in_usd_text.replace(/[^0-9.-]+/g,""));
    currency_in_eur_number = currency_in_usd_number * 0.8898;
    currency_in_eur_text = currency_in_eur_number.toLocaleString('en-US', { maximumFractionDigits: 2 })
    return "EUR".concat(currency_in_eur_text)
}
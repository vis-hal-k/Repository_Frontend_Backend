const accountId = 144553
let accountEmail = "hitesh@google.com"
var accountPassword = "12345"
accountCity = "Jaipur" // this is not a good practice

// accountId = 2 // cannot be changed 
accountEmail = "hc@hc.com"
accountPassword = "21212121"
accountCity = "Bengaluru"
/*
Prefer not to use var because of issue in block scope and functional scope.
*/
console.log(accountEmail);
console.table([accountId, accountEmail, accountPassword, accountCity]);
// Prefer not to use var because of issue in block scope and functional scope.
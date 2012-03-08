# Stocks

## Main goal

I'm using this to learn Django.

## Ultimate goal

Be able to take info from my ledger file and provide
performance information that can be slided and diced in many ways

## Freeform notes

It will be important to be able to tag transactions to see how
transactions with different tags compare in performance. (e.g.
index-based investing versus stock-picking etc). But, we'll have to
decide how to deal with cash in those situations.

So individual transactions can't really be tagged like that. It has to
be accounts which are tagged since accounts include both cash and
positions.

Maybe we can make those virtual accounts in some way. OK, that will
have to be decided later...

## First step goal

Keep track of my stock transactions and give me simple reports about
their performance. Are they up or down and by how many percentage
points?

### Datamodel (first stab)

Account
- user_id (assuming I have some user registration)
- name
- taxable? (boolean)

Securities
- symbol
- name
- type (stock/MF/ETF)
- exchange

Transactions
- timestamp
- action (BUY/SELL/DIV/INT/SS)
- security FK
- account FK
- shares
- price
- commission

Closing Prices
- security FK
- timestamp
- price

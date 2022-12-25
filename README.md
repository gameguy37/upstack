# Instructions

<aside>
❗ Please take no more than 2 hours on the coding part of this exercise. If you do not have a working version by then, this role is likely not a good fit.

</aside>

Write python code as for an AWS Lambda function that will ingest data like the provided data set, regularly every 6 hours. Your code does not need to deal with handoffs: assume the data is available locally at the time your code runs, and just ensure that your outputs are saved to a local `output` directory. No need to save them remotely or communicate them elsewhere. Please submit your code and your results directly to Greenhouse or by attaching them to an email. Please do *not* publish your answer to GitHub or similar sharing sites.

## Request from Data Consumer

> We need to match commissions data (rpm) to order data (sfdc) to understand our performance. Some noteworthy things about the way rpm and sfdc data use different terms for shared concepts:
> 

| sfdc term | rpm term |
| --- | --- |
| Advisory Partner | Agency |
| Advisor | Rep |
| Amount | Net billed |
| Date | Added |

> We want to report per month how much we are making (rpm data) and how much is getting added according to sfdc as well as answer the questions below. Regular output should include `Supplier`, `Registered`, `Billed`, by `Month`, in which “Registered” means it was logged in SFDC, and “Billed” means it was billed in RPM, and “Month” is YYYYMM
> 
> - `AccountID` has a granularity of `Supplier + Acct`. (Like you as a customer of your ISP have a unique ID in the ISP’s internal system, that’s what `Account` means in RPM; the ID according *to* the Supplier.)

# Analytical Questions

1. How many Suppliers were billed in August of 2022?
2. Which Supplier in which month had the largest positive discrepancy between what was registered and what was billed?

# Written Questions

1. What questions do you have for the business owner of this data?
2. What technical work should be done for your solution before it can be deployed?
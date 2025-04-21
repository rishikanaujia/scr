Here are example URLs for all 50 query patterns, using the single flexible endpoint:

1. Top Companies by Private Placement Count:
 On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?type=1&year=gte:2020&groupBy=companyName&select=companyName,COUNT(transactionId) as privatePlacementCount&orderBy=privatePlacementCount:desc&limit=1
```

2. Transaction Details with Type and Country:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?type=14&year=2021&country=131&select=transactionId,companyName,transactionSize,announcedDay,announcedMonth,announcedYear,transactionIdTypeName&orderBy=transactionSize:desc&limit=1
```

3. Transactions in Specific Industries and Country:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?industry=32,34&country=37&year=2023&select=transactionId,companyName,simpleIndustryDescription,country,announcedDay,announcedYear,transactionSize,currencyId&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc
```

4. Transactions by Country and Year:
 In This endpoint i am getting this error "invalid identifier 'SIMPLEINDUSTRYDESCRIPTION'"
```
/api/v1/transactions?country=76&year=2019&select=transactionId,companyName,simpleIndustryDescription,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc
```

5. Transactions with Complex Filtering:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?type=2&year=between:2018,2021&industry=63&country=ne:213&transactionSize=notnull:&select=transactionId,companyName,simpleIndustryDescription,transactionSize,currencyId,announcedDay,announcedMonth,announcedYear&orderBy=transactionSize:desc&limit=10
```

6. Company Acquisition Targets:
```
/api/v1/transactions?buyerId=29096&type=2&year=gte:2022&select=transactionId,targetCompanyName,buyerCompanyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc
```

7. Buyback Count by Industry and Period:
```
/api/v1/transactions?type=14&industry=60&year=between:2017,2019&select=COUNT(transactionId) as buyback_count
```

8. Transaction Value by Industry:
```
/api/v1/transactions?type=14&year=2017&country=7,16,99&currencyId=50&select=transactionId,companyName,country,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,SUM(transactionSize) OVER (PARTITION BY country) AS totalTransactionValue&groupBy=transactionId,companyName,country,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId&orderBy=country,announcedYear:desc,announcedMonth:desc,announcedDay:desc
```
```

/api/v1/transactions?type=14&year=2023&country=30&select=simpleIndustryDescription,SUM(transactionSize) as totalTransactionValue&groupBy=simpleIndustryDescription&orderBy=totalTransactionValue:desc
```

9. Transaction Value by Country (Window Function):
```
/api/v1/transactions?type=14&year=2017&country=7,16,99&currencyId=50&select=transactionId,companyName,country,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,SUM(transactionSize) OVER (PARTITION BY country) AS totalTransactionValue&orderBy=country,announcedYear:desc,announcedMonth:desc,announcedDay:desc
```

10. Distinct Industry Count:
```
/api/v1/transactions?type=14&year=2022&country=37&select=COUNT(DISTINCT(simpleIndustryDescription)) as industries_with_buybacks
```

11. Transactions by Industry and Year:
```
/api/v1/transactions?industry=69&year=2021&select=transactionId,companyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName,country&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc
```

12. Transactions by Industry, Country and Year:
```
/api/v1/transactions?industry=69&country=102&year=2021&select=transactionId,companyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName,country&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc
```

13. Transactions by Type, Industry, Year and Month:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?type=2,14&industry=6&year=2024&month=1&select=transactionId,companyName,simpleIndustryDescription,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName&orderBy=announcedDay:desc
```

14. Company Buybacks:
```
/api/v1/transactions?companyId=29096&type=14&select=transactionId,companyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyName,transactionIdTypeName&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc
```

15. Company Related Transactions:
```
/api/v1/transactions?involvedCompanyId=18749&select=transactionId,targetCompanyName,involvedCompanyName,announcedDay,announcedMonth,announcedYear,transactionIdTypeName,transactionToCompanyRelType,transactionSize,currencyId&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc&limit=5
```

16. Average Transaction Size:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?type=14&year=2022&month=3&currencyId=160&select=AVG(transactionsize)
```

17. Tech M&A Deal Count:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?type=2&year=2024&industry=58&select=COUNT(transactionId) as tech_ma_deals_in_2024
```

18. Mergers and Acquisitions Count:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?type=2&year=2022&industry=41&select=COUNT(transactionId) as number_of_mergers_and_acquisitions
```

19. Future Mergers Count:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?type=2&year=2025&industry=2&select=COUNT(transactionId) as number_of_mergers
```

20. Completed Transactions Count:
```
/api/v1/transactions?type=2&year=gte:2022&industry=50&statusId=2&select=COUNT(DISTINCT companyId) as CompletedTransactions
```

21. Bankruptcy Count:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?type=12&year=2024&industry=35&select=COUNT(transactionId) as BankruptcyCount
```

22. Transaction Count by Year:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?companyId=20765463&statusId=2&groupBy=announcedyear&select=announcedyear,COUNT(announcedyear)
```

23. Company Buyback Count:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?companyId=24937&type=14&select=COUNT(transactionId) as BuybackCount
```

24. Deal Count by Year and Type:
```
/api/v1/transactions?companyId=21401&year=2020,2021&groupBy=announcedYear,transactionIdTypeName&select=announcedYear,transactionIdTypeName,COUNT(transactionId) as dealCount&orderBy=announcedYear,transactionIdTypeName
```

25. Acquisitions by Company:
```
/api/v1/transactions?buyerId=284342&relationType=1&select=transactionId,targetCompanyName,buyerCompanyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc
```

26. Company Divestitures:
```
/api/v1/transactions?sellerId=112350&relationType=2&year=gte:2015&select=transactionId,targetCompanyName,sellerCompanyName,announcedDay,announcedMonth,announcedYear,transactionSize&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc
```

27. Advisors for Company:
```
/api/v1/transactions?involvedCompanyId=21719&select=DISTINCT(advisorCompanyName)
```

28. Legal Advisors for Company:
```
/api/v1/transactions?companyId=34903&type=2&advisorTypeId=2&select=advisorCompanyName
```

29. Buyback Advisors:
```
/api/v1/transactions?companyId=21835&type=14&select=advisorCompanyName
```

30. Advisor-Company Relationship Count:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?advisorId=398625&companyId=6882342&select=COUNT(transactionId)&groupBy=companyName
```

31. Largest Buyback Date:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?companyId=24937&type=14&select=announcedDay,announcedMonth,announcedYear&orderBy=transactionSize:desc&limit=1
```

32. Company Transaction Size:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?companyId=251994106&type=2&select=transactionSize,currencyId&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc&limit=1
```

33. Acquisition Count:
```
/api/v1/transactions?buyerId=21719&type=2&relationType=1&year=2018&select=COUNT(transactionId) AS acquisition_count
```

34. Top Industry by M&A:
```
/api/v1/transactions?year=2023&type=2&groupBy=simpleIndustryDescription&select=simpleIndustryDescription,COUNT(transactionId) as transactionCount&orderBy=transactionCount:desc&limit=1
```

35. Total Value by Industry and Currency:
```
/api/v1/transactions?industry=64&year=2023&type=2&currencyIsoCode=USD&select=SUM(transactionSize) as totalValue
```

36. Spin-Off Count:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?type=7&year=2024&select=COUNT(transactionId) as SpinOffCount
```

37. M&A Transactions by Industry:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?year=2022&industry=23&type=2&select=COUNT(transactionId) as number_of_ma_transactions
```

38. Fund Raise Count by Industry:
```
/api/v1/transactions?type=10&year=2022&industry=23&select=COUNT(transactionId) as number_of_fund_raises
```

39. Equity Buybacks Count:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?type=14&year=2022&industry=69&select=COUNT(transactionId) as equity_buybacks_count
```

40. Bankruptcy Count by Industry:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?type=12&year=2022&industry=56&select=COUNT(transactionId) as bankruptcyCount
```

41. Transaction Count for Company:
```
/api/v1/transactions?involvedCompanyId=972190&year=between:2021,2023&select=COUNT(transactionId)
```

42. Total Buyback Value:
  On Testing this endpoint getting correct result in API response
```
/api/v1/transactions?companyId=21719&type=14&year=gte:2005&select=SUM(transactionSize) as totalBuybackValue
```

43. Acquisitions by Company Since Year:
```
/api/v1/transactions?buyerId=21719&type=2&relationType=1&year=gte:2011&select=transactionId,targetCompanyName,buyerCompanyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc
```

44. Top Buybacks by Company:
```
/api/v1/transactions?type=14&country=213&industry=55,56&transactionSize=notnull:&select=companyName,transactionSize&orderBy=transactionSize:desc&limit=10
```

45. Largest Acquisition in Industry:
```
/api/v1/transactions?type=2&year=gte:2022&industry=56&country=213,37&select=transactionId,companyId,companyName,simpleIndustryDescription,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId&orderBy=transactionSize:desc&limit=1
```

46. Top Acquisition Countries:
```
/api/v1/transactions?type=2&relationType=1&year=2012&buyerCountry=37,213&groupBy=targetCountry&select=targetCountry,COUNT(transactionId) as acquisition_count&orderBy=acquisition_count:desc&limit=10
```

47. Cross-Industry Transactions:
```
/api/v1/transactions?relationType=1&buyerIndustry=61,62&buyerCountry=37,213&select=transactionId,targetCompanyName,buyerCompanyName,targetIndustryDescription,buyerIndustryDescription,buyerCountry,announcedDay,announcedMonth,announcedYear&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc
```

48. Industry Acquisition Count:
```
/api/v1/transactions?type=2&relationType=1&industry=56,61,62&groupBy=simpleIndustryDescription&select=simpleIndustryDescription,COUNT(transactionId) AS AcquisitionCount&orderBy=AcquisitionCount:desc
```

49. Pagination Example:
```
/api/v1/transactions?type=2&year=2023&page=1&page_size=10
```

50. Count Only Example:
```
/api/v1/transactions?type=14&year=2022&country=37&count_only=true
```

These URLs demonstrate how all the different query patterns can be handled by a single endpoint with the appropriate query parameters. The flexible design allows for combining any of these patterns for even more complex queries.
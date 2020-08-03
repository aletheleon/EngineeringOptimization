# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 01:09:58 2020

@author: alejandro leon hernandez
"""

from gurobipy import GRB, Model, quicksum
from csv import reader, writer
import pandas as pd
# from pprint import pprint

#DATA:
product_list = set()
order_list = set()
warehouse_list = set()

'''
    Creates p:
    Dictionary mapping product to its weight
'''
p = {}
with open("ProductWeight.csv") as win:
    weightreader = reader(win)
    next(weightreader)
    for product in weightreader:
        product_list.add(int(product[0]))
        p[int(product[0])] = int(product[1])
# print(p)

'''
    Creates o:
    Dictionary mapping (order, product) to the quantity of each product in an
    order.
'''
orders_df = pd.read_csv("Orders.csv", header = 0)
o = {}
for index, row in orders_df.iterrows():
    order_list.add(int(row[0]))
    o[row[0], row[1]] = row[2]
# pprint(o)

'''
    Creates d:
    Dictionary mapping (warehouse, order, product) to the price of fulfilling
    that product in the order for each warehouse.
'''
delivery_cost = pd.read_csv('DeliveryCost.csv', header = 0, index_col='Warehouse ID/OrderID')
d = {}
for warehouse_ID, row in delivery_cost.iterrows():
    warehouse_list.add(int(warehouse_ID))
    for order in range(len(row)):
        for product in product_list:
            d[warehouse_ID, order + 1, product] = p[product] * row[order]
# print(d)

'''
    Creates s:
    Dictionary mapping (warehouse, product) to the stocked quantity of a
    product that each warehouse has
'''
warehouses = pd.read_csv('Warehouses.csv', header = 0)
s = {}
for index, row in warehouses.iterrows():
    s[row[0], row[1]] = row[2]
# print(s)

#MODEL:
model = Model("Retail Model")

#VARIABLES:
x = model.addVars(product_list, order_list, warehouse_list, name = 'x')

#OBJECTIVE:
model.setObjective(quicksum(x[k, m, n] * d[n, m, k] for n, m, k in d.keys()), sense = GRB.MINIMIZE)

#CONSTRAINTS:
model.addConstrs(quicksum(x[k, m, n] for n in warehouse_list) == o[m, k] for m, k in o.keys())
model.addConstrs(quicksum(x[k, m, n] for m in order_list) <= s[n, k] for n in warehouse_list for k in product_list)

model.optimize()

'''
    Creates a csv file with the optimal objective value.
'''
with open("TR3_Hernandez_Nichols_Ulloa.csv", "w", newline="") as fout:
    write = writer(fout, quotechar="'", delimiter = ",")
    write.writerow(["Warehouse", "Order", "Product", "Product Quantity"])
    for k, m, n in x.keys():
        if (x[k, m, n].x > 0):
            write.writerow((k, m, n, x[k, m, n].x))

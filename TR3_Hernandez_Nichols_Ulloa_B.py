"""
@author ahernandez71
"""

import pandas as pd
from csv import writer
from gurobipy import GRB, Model, quicksum

# DATA:
order_df = pd.read_csv("Orders.csv")
warehouse_df = pd.read_csv("Warehouses.csv")
weights_df = pd.read_csv("ProductWeight.csv")
costs_df = pd.read_csv("DeliveryCost.csv")
fixed_df = pd.read_csv("FixedCosts.csv")

warehouses = list(range(1, costs_df.shape[0] + 1))
orders = list(range(1,costs_df.shape[1]))
products = list(range(1,weights_df.shape[0] + 1))

'''
Creates d:
Dictionary mapping (order, product) to the quantity of product in the order.
It is representative of demand.
'''
d={}
for index,row in order_df.iterrows():
    d[int(row['Order ID']), int(row['Product ID'])] = int(row['Quantity'])

'''
Creates s:
Dictionary mapping (warehouse, product) to the quantity of product in the
warehouse. It is representative of supply.
'''
s={}
for index,row in warehouse_df.iterrows():
    s[int(row['Warehouse ID']), int(row['Product ID'])] = int(row['Stock'])

'''
Creates w:
Dictionary mapping product to its weight in pounds. It is representative of
weight.
'''
w = {}
for index,row in weights_df.iterrows():
    w[int(row['Product ID'])] = int(row['Weight'])

'''
Creates c:
Dictionary mapping (warehouse, order) to the cost to fulfill one pound from
warehouse to order.
'''
c = {}
for index,row in costs_df.iterrows():
    for o in orders:
        c[int(row[0]),int(o)] = float(row[o])

'''
Creates f:
Dictionary mapping warehouse to the fixed cost of sending any product from that
warehouse.
'''
f = {}
for index,row in fixed_df.iterrows():
    for o in orders:
        f[int(row[0]),int(o)] = float(row[o])

# MODEL
m = Model('PartB')

# VARIABLES
# x is an integer variable representing the number of products k in order j are fulfilled by warehouse i
x = m.addVars(warehouses, orders, products, name = 'x', vtype=GRB.INTEGER)
# y is a binary variable representing whether warehouse i was used to fulfill an order
y = m.addVars(warehouses, orders, name = 'y', vtype=GRB.BINARY)

# OBJECTIVE
m.setObjective(quicksum(c[i,j] * w[k] * x[i,j,k] for i in warehouses for j in orders for k in products) +
               quicksum(f[i,j] * y[i,j] for i in warehouses for j in orders),
               sense = GRB.MINIMIZE)

# CONSTRAINTS
# Demand Constraint: Each order is fulfilled once
m.addConstrs(x.sum('*',j,k) == d[j,k] for (j,k) in d.keys())
# Warehouse Constraint: Number of product shipped from each warehouse is less than its stock
m.addConstrs(x.sum(i,'*',k) <= s[i,k] for (i,k) in s.keys())
'''
Warhouse Use Constraint:
Shipment of a product from a warehouse requires the use of the warehouse variable to account the fixed cost.
Since warehouse use is accounted for by variable y, the Big M is set to be the stock constraint.
'''
m.addConstrs(x[i,j,k] <= s[i,k] * y[i,j] for i in warehouses for j in orders for k in products if (i,k) in s.keys())

m.optimize()

for j in orders:
    for i in warehouses:
        for k in products:
            if x[i,j,k].x > 0:
                print('Order %i was sent %f units of of Product %i from Warehouse %i' % ( j, x[i,j,k].x, k, i))

print(m.objVal)

"""
with open("Part B Solution.csv", "w", newline="") as fout:
    write = writer(fout, quotechar="'", delimiter = ",")
    write.writerow(["Warehouse", "Order", "Product", "Product Quantity"])
    for i, j, k in x.keys():
        if (x[i,j,k].x > 0):
            write.writerow((i, j, k, round(x[i,j,k].x)))
    write.writerow([])
    write.writerow(["Optimal Solution:","","", m.objVal])
"""

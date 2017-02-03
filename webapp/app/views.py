from __future__ import print_function # In python 2.7

from app import app
from flask import jsonify
from flask import render_template
from flask import request
import sys
import json
import boto3

dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id='dummy-access-id',
                          aws_secret_access_key='dummy-secret-access-key',
                          region_name='us-west-2',
                          endpoint_url='http://localhost:8000')  # Set DynamoDB connection (local)

dynamo_table = dynamodb.Table('venmo-graph-analytics-dev')  # Set DynamoDB table


@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Miguel'}  # fake user
    mylist = [1, 2, 3, 4]
    # return render_template("index.html", title='Home', list=mylist, )
    return render_template("index.html", title='Home', user=user)

@app.route('/usersearch')
def usersearch():
    return render_template("usersearch.html")

@app.route("/usersearch", methods=['POST'])
def username_post():
    # username = request.form["username"]
    id = request.form["username"]
    print("Received request: " + id)

    response = dynamo_table.get_item(
        Key={
            'id': int(id),
        }
    )

    num_transactions = response['Item']['num_transactions']
    reds = response['Item']['red_neighbors']
    blues = response['Item']['blue_neighbors']
    yellows = response['Item']['yellow_neighbors']
    greens = response['Item']['green_neighbors']
    blacks = response['Item']['black_neighbors']

    user = response['Item']['id']
    red_neighbors = set([x for x in reds if x is not None])
    blue_neighbors = set([x for x in blues if x is not None])
    yellow_neighbors = set([x for x in yellows if x is not None])
    green_neighbors = set([x for x in greens if x is not None])
    black_neighbors = set([x for x in blacks if x is not None])

    red_edges = bfs(user, red_neighbors, 'red_neighbors')
    blue_edges = bfs(user, blue_neighbors, 'blue_neighbors')
    yellow_edges = bfs(user, yellow_neighbors, 'yellow_neighbors')
    green_edges = bfs(user, green_neighbors, 'green_neighbors')
    black_edges = bfs(user, black_neighbors, 'black_neighbors')

    num_reds = len([x for x in reds if x is not None])
    num_blues = len([x for x in blues if x is not None])
    num_yellows = len([x for x in yellows if x is not None])
    num_greens = len([x for x in greens if x is not None])
    num_blacks = len([x for x in blacks if x is not None])

    # print("Query result: " + response)
    response_dict = {"firstname": response['Item']['firstname'],
                     "lastname": response['Item']['lastname'],
                     "username": response['Item']['username'],
                     "num_transactions": num_transactions,
                     "ratio_reds": float(num_reds / num_transactions),
                     "ratio_blues": float(num_blues / num_transactions),
                     "ratio_yellows": float(num_yellows / num_transactions),
                     "ratio_greens": float(num_greens / num_transactions),
                     "ratio_blacks": float(num_blacks / num_transactions),
                     "red_edges": red_edges,
                     "blue_edges": blue_edges,
                     "yellow_edges": yellow_edges,
                     "green_edges": green_edges,
                     "black_edges": black_edges,
                     }
    return render_template("userinfo.html", output=response_dict)

@app.route('/realtime')
def realtime():
    return render_template("realtime.html")


@app.route('/api/<username>')
def get_user(username):

    # Getting an item
    response = dynamo_table.get_item(
        Key={
            'id': username,
        }
    )
    item = jsonify(response['Item'])
    print(item)
    return item


def bfs(user, deg1_neighbors, color_neighbors):
    edge_list = []
    for deg1_neighbor in deg1_neighbors:
        edge = sorted([int(user), int(deg1_neighbor)])
        edge_list.append(tuple(edge))

        response = dynamo_table.get_item(Key={'id': int(deg1_neighbor)})
        deg2_neighbors = response['Item'][color_neighbors]
        deg2_neighbors = set([x for x in deg2_neighbors if x is not None])
        for deg2_neighbor in deg2_neighbors:
            edge = sorted([int(deg1_neighbor), int(deg2_neighbor)])
            edge_list.append(tuple(edge))
    return set(edge_list)
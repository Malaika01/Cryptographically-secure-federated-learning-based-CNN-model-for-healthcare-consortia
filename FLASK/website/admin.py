
import torch
import numpy as np
import io
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from . import db

from .models import User
from .models import FL_Model
from tqdm import tqdm
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
import torchvision.transforms as transforms
from medmnist import INFO, Evaluator
from dataclasses import dataclass
import random



# Define the CNN class that inherits from the nn.Module class
class CNN(nn.Module):
    def __init__(self, in_channels, num_classes):
        super(CNN, self).__init__()

        # Define the first convolutional layer with 16 filters of size 3x3
        # followed by a batch normalization layer and a ReLU activation function
        self.layer1 = nn.Sequential(
            nn.Conv2d(in_channels, 16, kernel_size=3),
            nn.BatchNorm2d(16),
            nn.ReLU())

        # Define the second convolutional layer with 16 filters of size 3x3
        # followed by a batch normalization layer, a ReLU activation function, and a max pooling layer with kernel size 2x2 and stride 2
        self.layer2 = nn.Sequential(
            nn.Conv2d(16, 16, kernel_size=3),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))

        # Define the third convolutional layer with 64 filters of size 3x3
        # followed by a batch normalization layer and a ReLU activation function
        self.layer3 = nn.Sequential(
            nn.Conv2d(16, 64, kernel_size=3),
            nn.BatchNorm2d(64),
            nn.ReLU())

        # Define the fourth convolutional layer with 64 filters of size 3x3
        # followed by a batch normalization layer and a ReLU activation function
        self.layer4 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3),
            nn.BatchNorm2d(64),
            nn.ReLU())

        # Define the fifth convolutional layer with 64 filters of size 3x3 and padding of 1
        # followed by a batch normalization layer, a ReLU activation function, and a max pooling layer with kernel size 2x2 and stride 2
        self.layer5 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))

        # Define the fully connected layers with 128 units each and ReLU activation functions
        # followed by a linear layer with num_classes units
        self.fc = nn.Sequential(
            nn.Linear(64 * 4 * 4, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes))

    # Define the forward pass method for the CNN
    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.layer5(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x
    
data_flag = 'chestmnist'
download = True

# get the information of the current dataset
info = INFO[data_flag]
task = info['task']
n_channels = info['n_channels']
n_classes = len(info['label'])



from dataclasses import dataclass
import random

inf = float("inf")

@dataclass
class PrimeGaloisField:
    prime: int

    def __contains__(self, field_value: "FieldElement") -> bool:
        # called whenever you do: <FieldElement> in <PrimeGaloisField>
        return 0 <= field_value.value < self.prime
    
@dataclass
class FieldElement:
    value: int
    field: PrimeGaloisField

    def __repr__(self):
        return "0x" + f"{self.value:x}".zfill(64)
        
    @property
    def P(self) -> int:
        return self.field.prime
    
    def __add__(self, other: "FieldElement") -> "FieldElement":
        return FieldElement(
            value=(self.value + other.value) % self.P,
            field=self.field
        )
    
    def __sub__(self, other: "FieldElement") -> "FieldElement":
        return FieldElement(
            value=(self.value - other.value) % self.P,
            field=self.field
        )
    def __rmul__(self, scalar: int) -> "FieldValue":
        return FieldElement(
            value=(abs(self.value) * scalar) % self.P,
            field=self.field
        )

    def __mul__(self, other: "FieldElement") -> "FieldElement":
        return FieldElement(
            value=(self.value * other.value) % self.P,
            field=self.field
        )
        
    def __pow__(self, exponent: int) -> "FieldElement":
        return FieldElement(
            value=pow(self.value, exponent, self.P),
            field=self.field
        )

    def __truediv__(self, other: "FieldElement") -> "FieldElement":
        other_inv = other ** -1
        return self * other_inv
@dataclass
class EllipticCurve:
    a: int
    b: int

    field: PrimeGaloisField
    
    def __contains__(self, point: "Point") -> bool:
        x, y = point.x, point.y
        return y ** 2 == x ** 3 + self.a * x + self.b

    def __post_init__(self):
        # Encapsulate int parameters in FieldElement
        self.a = FieldElement(self.a, self.field)
        self.b = FieldElement(self.b, self.field)
    
        # Check for membership of curve parameters in the field.
        if self.a not in self.field or self.b not in self.field:
            raise ValueError

@dataclass
class Point:
    x: int
    y: int
    
    curve: EllipticCurve
    
    
    def __post_init__(self):
        # Ignore validation for I
        if self.x is None and self.y is None:
            return

        # Encapsulate int coordinates in FieldElement
        self.x = FieldElement(self.x, self.curve.field)
        self.y = FieldElement(self.y, self.curve.field)

        # Verify if the point satisfies the curve equation
        if self not in self.curve:
            raise ValueError         
    def __add__(self, other):

        if self == I:
            return other

        if other == I:
            return self
        
        if self.x == other.x and self.y == (-1 * other.y):
            return I
        if self.x != other.x:
            x1, x2 = self.x, other.x
            y1, y2 = self.y, other.y

            s = (y2 - y1) / (x2 - x1)
            x3 = s ** 2 - x1 - x2
            y3 = s * (x1 - x3) - y1

            return self.__class__(
                x=x3.value,
                y=y3.value,
                curve=curve256
            )

        if self == other and self.y == inf:
            return I

        if self == other:
            x1, y1, a = self.x, self.y, self.curve.a

            s = (3 * x1 ** 2 + a) / (2 * y1)
            x3 = s ** 2 - 2 * x1
            y3 = s * (x1 - x3) - y1

            return self.__class__(
                x=x3.value,
                y=y3.value,
                curve=curve256
            )
   

    def __rmul__(self, scalar: int) -> "Point":
        
        # Optimized approach using binary expansion
        current = self
        result = I
        while scalar:
            if scalar & 1:  # same as scalar % 2
                result = result + current
            current = current + current  # point doubling
            scalar >>= 1  # same as scalar / 2
        return result

# Parameters for the Elliptic Curve being used i.e y² = x³ + 2x + 2
p = 17
field = PrimeGaloisField(p)
A= 2
B= 2
curve256 = EllipticCurve(A,B,field)
I = Point(None,None,curve256)


    



admin = Blueprint('admin', __name__)

@admin.route('/aggregate_model', methods=['GET', 'POST'])
@login_required
def aggregate_model():
    print("The button was clicked.")
    if request.method == 'GET':
        print("------IT IS GET------")
        # Call load_hospital_weights function
        print("-----------CALLING FUNCTION-------")
        load_hospital_weights()
        return redirect(url_for('admin.success'))
    else:
        return render_template('aggregate_model.html', user=current_user)

@admin.route('/view_pending_requests')
@login_required
def view_pending_requests():
    # Add your code here for viewing pending hospital requests
    return render_template('view_pending_requests.html', user=current_user)


    
    
    
   
        

def load_hospital_weights():
   # Retrieve all User objects from the database
    users = User.query.all()

    # Extract hospital weights from each User object and store in a list
    weights = []
    for user in users:
        if user.hospitalWeights is not None:
            buffer = io.BytesIO(user.hospitalWeights)
            weights.append(torch.load(buffer))
    
    m1 = weights[0]
    m2 = weights[1]
    m3 = weights[2]

    

    w1 = []
    w2 = []
    w3 = []

    # Iterate over all keys in the state dictionary
    for key in m1:
        tensor = m1[key]
        # Iterate over all elements of the tensor
        for i in range(tensor.numel()):
            w1.append(int(tensor.view(-1)[i]* 100000))

    

    #Iterate over all keys in the state dictionary
    for key in m2:
        tensor = m2[key]
        # Iterate over all elements of the tensor
        for i in range(tensor.numel()):
            w2.append(int(tensor.view(-1)[i]* 100000))
    
    

    # Iterate over all keys in the state dictionary
    for key in m3:
        tensor = m3[key]
        # Iterate over all elements of the tensor
        for i in range(tensor.numel()):
            w3.append(int(tensor.view(-1)[i] * 100000))  
            #w3.append(int(tensor.view(-1)[i] ))
    
            
    gx = 5
    gy = 1
    G = Point(gx,gy,curve256)

    

    px= 3
    py= 1
    P = Point(px,py,curve256)

    r1 = random.randint(1, p)
    r2 = random.randint(1, p)
    r3 = r1 + r2

    nP = Point(px,(p-py),curve256)
    nG = Point(gx,(p-gy),curve256)

    R1 = r1 * P
    R2 = r2 * P 
    R3 = r3 * nP

    Z1 = []
    Z2 = []
    Z3 = []
    
    for i in range(len(w1)):
        if w1[i]<0:
            val=abs(r1 + w1[i]) * G
            if val.x is not None and val.y is not None:
                
                nVal=Point(val.x.value,p-val.y.value,curve256)
                Z1.append(nVal)
            else:
                #print("identity")
                Z1.append(I)
        else:
            Z1.append(abs(r1 + w1[i]) * G)
        #print(Z1[i])

    for i in range(len(w1)):
        #print(w2[i])
        if w2[i]<0:
            val=abs(r2 + w2[i]) * G
            
            if val.x is not None and val.y is not None:
                nVal=Point(val.x.value,p-val.y.value,curve256)
                Z2.append(nVal)
            else:
                Z2.append(I)
        else:
            Z2.append(abs(r2 + w2[i]) * G)
        #print(Z2[i])
        
        #nr = -r3 + w3
        
    nr = []
    for i in range(len(w1)):
        nr.append(-r3+w3[i])
        
    for i in range(len(w1)):
        if nr[i]>0:
            nr[i]=-nr[i]
            Z3.append(-nr[i]* nG)
            if Z3[i].x is None or Z3[i].x.value is None:
                Z3[i]=I
            else:
                Z3[i]=Point(Z3[i].x.value,p-Z3[i].y.value,curve256)
        else:
            Z3.append(-nr[i]* nG)
            #print(i)
        #print(Z3[i])

    #Rsum
    Rsum = R1 + R2 + R3

    referencePoint=[]
    for i in range(len(w1)):
        referencePoint.append(Z1[i] + Z2[i] + Z3[i])
        #print("Reference point: \n",referencePoint[i])
        #print("\n")

    basePoint = G
    
    #Cycle of Ps
    points = []
    points.append(P)
    check = False
    temp = basePoint
    while check == False:
        temp += basePoint
        if(temp == I):
            check = True
        points.append(temp)
    #print("Length of cycle:",len(points),'\n')

    # Create a new empty state dictionary with the same structure as the original state dictionary
    aggregatedModel = {}
    for key in m1:
        tensor = m1[key]
        aggregatedModel[key] = torch.zeros_like(tensor)
    
    aggregatedWeights = []
    
    iteration = 0
    for r in range(len(w1)):
        #print(w1[r],w2[r],w3[r],"\n")
        for i in points:
    #         print("Point ",iteration+1,":")
    #         print(i)
            if(referencePoint[r] == i):
                num = points.index(i)
            iteration += 1
        #print("\nReference Point matches the point",num+1,"in the cycle")
        aggregatedWeights.append( (((num+1)/3)/100000) )
        
    


    
    # Convert the aggregatedWeights list to a tensor
    values_tensor = torch.tensor(aggregatedWeights)
    
    # Iterate over all keys in the state dictionary
    index = 0
    for key in aggregatedModel:
        tensor = aggregatedModel[key]
        # Compute the number of elements in the tensor
        num_elements = tensor.numel()
        # Reshape the 1D array of values to match the shape of the tensor
        values_reshaped = values_tensor[index:index+num_elements].view(tensor.shape)
        # Set the values of the tensor to the values from the array
        tensor.copy_(values_reshaped)
        # Increment the index to point to the next set of values
        index += num_elements

    # Call the function to get the PyTorch model object
    model = CNN(in_channels=n_channels, num_classes=n_classes)
    model.load_state_dict(aggregatedModel)

    # Save the state_dict of the PyTorch model to a buffer
    buffer = io.BytesIO()
    torch.save(model.state_dict(), buffer)
    buffer.seek(0)
    byte_stream = buffer.read()

    # Check if the FL_Model table has any records
    fl_model = FL_Model.query.first()

    # If there are no records, create a new row and save the model weights
    if fl_model is None:
        fl_model = FL_Model(aggregatedWeights=byte_stream)
        db.session.add(fl_model)
    # Otherwise, update the weights of the first row
    else:
        fl_model.aggregatedWeights = byte_stream

    # Commit the changes to the database
    db.session.commit()



@admin.route('/success')
@login_required
def success():
    return render_template('success.html', user=current_user)

#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install coordinates


# In[45]:


from dataclasses import dataclass
import random


# In[46]:


inf = float("inf")


# In[47]:


@dataclass
class PrimeGaloisField:
    prime: int

    def __contains__(self, field_value: "FieldElement") -> bool:
        # called whenever you do: <FieldElement> in <PrimeGaloisField>
        return 0 <= field_value.value < self.prime


# In[48]:


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
            value=(self.value * scalar) % self.P,
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


# In[49]:


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


# In[50]:


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
        #################################################################
        # Point Addition for P₁ or P₂ = I   (identity)                  #
        #                                                               #
        # Formula:                                                      #
        #     P + I = P                                                 #
        #     I + P = P                                                 #
        #################################################################
        if self == I:
            return other

        if other == I:
            return self

        #################################################################
        # Point Addition for X₁ = X₂   (additive inverse)               #
        #                                                               #
        # Formula:                                                      #
        #     P + (-P) = I                                              #
        #     (-P) + P = I                                              #
        #################################################################
        if self.x == other.x and self.y == (-1 * other.y):
            return I

        #################################################################
        # Point Addition for X₁ ≠ X₂   (line with slope)                #
        #                                                               #
        # Formula:                                                      #
        #     S = (Y₂ - Y₁) / (X₂ - X₁)                                 #
        #     X₃ = S² - X₁ - X₂                                         #
        #     Y₃ = S(X₁ - X₃) - Y₁                                      #
        #################################################################
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

        #################################################################
        # Point Addition for P₁ = P₂   (vertical tangent)               #
        #                                                               #
        # Formula:                                                      #
        #     S = ∞                                                     #
        #     (X₃, Y₃) = I                                              #
        #################################################################
        if self == other and self.y == inf:
            return I

        #################################################################
        # Point Addition for P₁ = P₂   (tangent with slope)             #
        #                                                               #
        # Formula:                                                      #
        #     S = (3X₁² + a) / 2Y₁         .. ∂(Y²) = ∂(X² + aX + b)    #
        #     X₃ = S² - 2X₁                                             #
        #     Y₃ = S(X₁ - X₃) - Y₁                                      #
        #################################################################
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
        # Naive approach:
        #
        # result = I
        # for _ in range(scalar):  # or range(scalar % N)
        #     result = result + self
        # return result
        
        # Optimized approach using binary expansion
        current = self
        result = I
        while scalar:
            if scalar & 1:  # same as scalar % 2
                result = result + current
            current = current + current  # point doubling
            scalar >>= 1  # same as scalar / 2
        return result
    


# In[66]:


# Parameters for the Elliptic Curve being used i.e y² = x³ + 2x + 2
P = (0x11)
p = 17
field = PrimeGaloisField(P)
A = 2
B = 1
curve256 = EllipticCurve(A,B,field)
I = Point(None,None,curve256)


# In[68]:


# G(0,1)
gx = 0
gy = 1
G = Point(gx,gy,curve256)
#P(0,-1)
px = 0
py = -1
P = Point(px,py,curve256)

r1 = random.randint(1, 17)
r2 = random.randint(1, 17)
r3 = r1 + r2
w1 = 3
w2 = 2
w3 = 1
print("W:",w1,w2,w3)

# nP = Point(px,(p-py)%p,curve256)
#nG = Point(gx,(p-gy)%p,curve256)

nP = Point(px,(p-py)%p,curve256)
nG = Point(gx,(p-gy)%p,curve256)

#print("NP",np)
R1 = P
R2 = r2 * P 
R3 = r3 * nP
#print("R:",R1,R2,R3)


Z1 = (r1 + w1) * G
Z2 = (r2 + w2) * G 
#--------------
nr = -r3 + w3 
#--------------
Z3 = -nr * nG

Rsum = R1 + R2 + R3
referencePoint = Z1 + Z2 + Z3

print("Reference point: \n",referencePoint)
basePoint = P

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
print("Length of cycle:",len(points),'\n')
print("Points in the cycle:")
num = 0

iteration = 0
for i in points:
    print("Point ",iteration+1,":")
    print(i)
    if(referencePoint == i):
        num = points.index(i)
    iteration += 1
print("\nReference Point matches the point",num+1,"in the given cycle")


# In[ ]:





# In[ ]:





# In[ ]:





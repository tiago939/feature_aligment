import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
import os, random, sys, math
import numpy as np
import matplotlib.pyplot as plt
import networks

device = 'cuda'
batch_size = 25
Z = 128
T = 1

transform_train = transforms.Compose([
    transforms.ToTensor(),
])

trainset = torchvision.datasets.MNIST(
    root='./data', train=False, download=True, transform=transform_train)
trainloader = torch.utils.data.DataLoader(
    trainset, batch_size=batch_size, shuffle=False, num_workers=1)


model = networks.Encoder(Z).to(device)
generator = networks.Generator().to(device)
checkpoint = torch.load('./checkpoint_fa/ckpt.pth')
model.load_state_dict(checkpoint['encoder_state_dict'])
generator.load_state_dict(checkpoint['generator_state_dict'])

model.eval()
generator.eval()

L = len(model.encoder)
for batch_idx, (inputs,targets) in enumerate(trainloader):

    if batch_idx > 0:
        break

    x = inputs.to(device)

    shapes = []
    for layer in range(L):
        shapes.append(x.shape)
        x = model.encoder[layer](x)

    x = x.detach()
    for layer in range(L-1,-1,-1):
        u = torch.zeros(shapes[layer], device=device)
        u.requires_grad_(True)

        fu = model.encoder[layer](u)
        cost = 0.5*torch.sum( (x - fu)**2.0)
        u = u - torch.autograd.grad(cost, u, retain_graph=True, create_graph=True)[0]

        layers=[1,3,5,7,10] #layers with arsinh function
        if layer in layers:
            u = torch.sinh(u)

        x = u.detach()

    u = torch.tanh(u)

plt.clf()
grid_img = torchvision.utils.make_grid(u.cpu(), nrow=5)
plt.axis('off')
plt.imshow(grid_img.permute(1, 2, 0))
plt.show()

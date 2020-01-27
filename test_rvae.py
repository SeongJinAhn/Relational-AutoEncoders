import argparse
import pickle
import torch.utils.data
import Methods.rvae as rvae
from Methods.models import load_datasets, AE_CelebA, AE_MNIST


parser = argparse.ArgumentParser(description='VAE Example')
parser.add_argument('--batch-size', type=int, default=100, metavar='N',
                    help='input batch size for training (default: 512)')
parser.add_argument('--epochs', type=int, default=50, metavar='N',
                    help='number of epochs to train (default: 10)')
parser.add_argument('--no-cuda', action='store_true', default=False,
                    help='enables CUDA training')
parser.add_argument('--seed', type=int, default=1, metavar='S',
                    help='random seed (default: 1)')
parser.add_argument('--log-interval', type=int, default=10, metavar='N',
                    help='how many batches to wait before logging training status')
parser.add_argument('--source-data', type=str, default='MNIST',
                    help='data name')
parser.add_argument('--datapath', type=str, default='Data',
                    help='data path')
parser.add_argument('--resultpath', type=str, default='Results/rvae',
                    help='result path')
parser.add_argument('--landmark-interval', type=int, default=5,
                    help='interval for recording')
parser.add_argument('--x-dim', type=int, default=784,
                    help='input dimension')
parser.add_argument('--z-dim', type=int, default=8,
                    help='latent dimension')
parser.add_argument('--nc', type=int, default=1,
                    help='the number of channels')
parser.add_argument('--gamma', type=float, default=500.0,
                    help='the weight of regularizer')
parser.add_argument('--lr', type=float, default=5e-5,
                    help='learning rate')
parser.add_argument('--beta', type=float, default=0.1,
                    help='the weight of regularizer')
parser.add_argument('--model-type', type=str, default='probabilistic',
                    help='the type of model')
parser.add_argument('--loss-type', type=str, default='BCE',
                    help='the type of loss')
args = parser.parse_args()
args.cuda = not args.no_cuda and torch.cuda.is_available()
torch.manual_seed(args.seed)
device = torch.device("cuda" if args.cuda else "cpu")
print(device)

if __name__ == '__main__':
    for src in ['CelebA']:
        print(src)
        args.source_data = src
        if src == 'MNIST':
            args.x_dim = int(28 * 28)
            args.z_dim = 8
            args.nc = 1
            args.loss_type = 'MSE'
            args.landmark_interval = 5
            model = AE_MNIST(z_dim=args.z_dim, nc=args.nc, model_type=args.model_type)
            prior = rvae.Prior(data_size=[10, args.z_dim])
        else:
            args.x_dim = int(64 * 64)
            args.z_dim = 64
            args.nc = 3
            args.loss_type = 'MSE'
            args.landmark_interval = 5
            model = AE_CelebA(z_dim=args.z_dim, nc=args.nc, model_type=args.model_type)
            prior = rvae.Prior(data_size=[10, args.z_dim])

        src_loaders = load_datasets(args=args)
        loss = rvae.train_model(model, prior, src_loaders['train'], src_loaders['val'], device, args)
        model = model.to('cpu')
        prior = prior.to('cpu')
        torch.save(model.state_dict(), '{}/model_{}.pt'.format(args.resultpath, args.source_data))
        torch.save(prior.state_dict(), '{}/prior_{}.pt'.format(args.resultpath, args.source_data))
        with open('{}/loss_{}.pkl'.format(args.resultpath, args.source_data), 'wb') as f:
            pickle.dump(loss, f)
        print('\n')

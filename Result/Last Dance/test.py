from sklearn.mixture import GaussianMixture

key_mixture = GaussianMixture(n_components=args.gmm_num_components, random_state=args.seed).fit(x_key.cpu().detach().numpy())
encoded_mixture = GaussianMixture(n_components=args.gmm_num_components, random_state=args.seed).fit(x_encoded.cpu().detach().numpy())
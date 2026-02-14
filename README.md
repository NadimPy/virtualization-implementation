# Virtualization-implementation

## About The Project

Ec2 and Google Compute Engine are fascinating cloud services, this project tries to imitate these services to provision VMs from known linux images on demand. It consists mainly of a fastapi backend that uses libvirt to interface with KVM to provision VMs on demand.
* Infrastructure 
   * Implementation: the infrascture implementation will be documented to show how to configure a server to use KVM and libvirt.

**Backend**
   * Auth: As this is a simple project, authentication will simply rely on API headers. We can view for the future the use of IAM based roles using Keycloak
   * Simple API endpoints shown in `vm-dashboard/main.py`

## Getting Started



### Prerequisites



### Installation



## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

## Roadmap

- [ ] Implement fastapi backend logic + dashboard that fetches from this backend (without libvirt)
- [ ] Add to endpoints libvirt support
- [ ] Feature 3
    - [ ] Nested Feature

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the project_license. See `LICENSE.txt` for more information.

## Contact

## Acknowledgments


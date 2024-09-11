COLLECTION_NAME=gebz97.oradb
TAR_FILE=$(COLLECTION_NAME)-1.0.0.tar.gz
COLLECTION_PATH=$(HOME)/.ansible/collections/ansible_collections/gebz97

.PHONY: build remove install reinstall

# Build the collection (create tarball)
build:
	@echo "Building the collection..."
	ansible-galaxy collection build
	@echo "Build complete: $(TAR_FILE)"

# Remove the collection from the Ansible collections path
remove:
	@echo "Removing the collection..."
	rm -rf $(COLLECTION_PATH)
	@echo "Collection removed from $(COLLECTION_PATH)"

# Install the collection from the tarball
install: build
	@echo "Installing the collection..."
	ansible-galaxy collection install $(TAR_FILE)
	@echo "$(COLLECTION_NAME) was installed successfully."

# Remove, build and install the collection
reinstall: remove install
	@echo "Reinstall complete."

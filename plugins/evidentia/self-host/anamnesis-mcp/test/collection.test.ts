import { describe, it, expect } from "vitest";
import {
  LEGACY_COLLECTION,
  isValidCollection,
  resolveWriteCollection,
  resolveScopedCollection,
  requireCollection,
  isScratchCollection,
  CollectionRequiredError,
  InvalidCollectionError,
} from "../src/collection.js";

describe("collection contract", () => {
  it("accepts {plugin}:{run|sess|lib}:{id}", () => {
    expect(isValidCollection("evidentia:run:aabbccddeeff")).toBe(true);
    expect(isValidCollection("cureolex:lib:mevzuat-3960")).toBe(true);
    expect(isValidCollection("vekayinuvis:sess:01")).toBe(true);
  });

  it("rejects invented kinds and empty pieces", () => {
    expect(isValidCollection("evidentia:scratch:aabbccddeeff")).toBe(false);
    expect(isValidCollection("evidentia:run:")).toBe(false);
    expect(isValidCollection("_legacy")).toBe(false);
    expect(isValidCollection("")).toBe(false);
  });

  it("write-side missing collection becomes _legacy", () => {
    expect(resolveWriteCollection(undefined)).toBe(LEGACY_COLLECTION);
    expect(resolveWriteCollection("")).toBe(LEGACY_COLLECTION);
  });

  it("write-side invalid collection throws (never silent-bucket)", () => {
    expect(() => resolveWriteCollection("not-a-collection")).toThrow(InvalidCollectionError);
  });

  it("requireCollection errors when omitted", () => {
    expect(() => requireCollection(undefined, "hybrid_query")).toThrow(CollectionRequiredError);
    expect(requireCollection("evidentia:run:aabbccddeeff", "hybrid_query"))
      .toBe("evidentia:run:aabbccddeeff");
  });

  it("run/sess are scratch; lib is not", () => {
    expect(isScratchCollection("evidentia:run:aabbccddeeff")).toBe(true);
    expect(isScratchCollection("evidentia:sess:aabbccddeeff")).toBe(true);
    expect(isScratchCollection("evidentia:lib:handbook")).toBe(false);
    expect(isScratchCollection(LEGACY_COLLECTION)).toBe(false);
  });

  it("scoped resolve accepts _legacy for observe/forget", () => {
    expect(resolveScopedCollection("_legacy")).toBe(LEGACY_COLLECTION);
    expect(resolveScopedCollection("")).toBeUndefined();
  });
});
